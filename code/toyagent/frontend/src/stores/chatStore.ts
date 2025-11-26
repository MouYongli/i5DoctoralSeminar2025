import { create } from "zustand";
import type { Message, Conversation, WorkflowMeta } from "@/types";
import { toMessage, toConversation } from "@/types/chat";
import * as api from "@/lib/api";

interface ChatState {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  currentChatId: string | null;
  messages: Message[];
  currentWorkflow: WorkflowMeta | null;
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;

  // Sync actions
  setConversations: (conversations: Conversation[]) => void;
  setCurrentConversation: (conversation: Conversation | null) => void;
  setCurrentChatId: (chatId: string | null) => void;
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  appendToLastMessage: (content: string) => void;
  setCurrentWorkflow: (workflow: WorkflowMeta | null) => void;
  setLoading: (loading: boolean) => void;
  setStreaming: (streaming: boolean) => void;
  setError: (error: string | null) => void;

  // Async actions
  loadConversations: () => Promise<void>;
  loadChat: (chatId: string) => Promise<void>;
  createChat: (title: string) => Promise<string>;
  deleteChat: (chatId: string) => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  currentConversation: null,
  currentChatId: null,
  messages: [],
  currentWorkflow: null,
  isLoading: false,
  isStreaming: false,
  error: null,

  // Sync actions
  setConversations: (conversations) => set({ conversations }),

  setCurrentConversation: (conversation) =>
    set({ currentConversation: conversation }),

  setCurrentChatId: (chatId) => set({ currentChatId: chatId }),

  setMessages: (messages) => set({ messages }),

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  updateMessage: (id, updates) =>
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, ...updates } : m
      ),
    })),

  appendToLastMessage: (content) =>
    set((state) => {
      const messages = [...state.messages];
      const lastMessage = messages[messages.length - 1];
      if (lastMessage && lastMessage.role === "assistant") {
        messages[messages.length - 1] = {
          ...lastMessage,
          content: lastMessage.content + content,
        };
      }
      return { messages };
    }),

  setCurrentWorkflow: (workflow) => set({ currentWorkflow: workflow }),

  setLoading: (isLoading) => set({ isLoading }),
  setStreaming: (isStreaming) => set({ isStreaming }),
  setError: (error) => set({ error }),

  // Async actions
  loadConversations: async () => {
    const { setLoading, setError, setConversations } = get();
    setLoading(true);
    setError(null);
    try {
      const chats = await api.listChats();
      setConversations(chats.map(toConversation));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load conversations");
    } finally {
      setLoading(false);
    }
  },

  loadChat: async (chatId: string) => {
    const { setLoading, setError, setMessages, setCurrentChatId, setCurrentConversation } = get();
    setLoading(true);
    setError(null);
    try {
      const chat = await api.getChat(chatId);
      setCurrentChatId(chatId);
      setCurrentConversation({
        id: chat.id,
        title: chat.title,
        createdAt: new Date(chat.created_at),
        updatedAt: new Date(chat.updated_at),
        messageCount: chat.messages.length,
      });
      setMessages(chat.messages.map(toMessage));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load chat");
    } finally {
      setLoading(false);
    }
  },

  createChat: async (title: string) => {
    const { setLoading, setError, loadConversations, setCurrentChatId, setMessages } = get();
    setLoading(true);
    setError(null);
    try {
      const chat = await api.createChat(title);
      await loadConversations();
      setCurrentChatId(chat.id);
      setMessages([]);
      return chat.id;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create chat");
      throw e;
    } finally {
      setLoading(false);
    }
  },

  deleteChat: async (chatId: string) => {
    const { setError, loadConversations, currentChatId, setCurrentChatId, setMessages } = get();
    try {
      await api.deleteChat(chatId);
      await loadConversations();
      if (currentChatId === chatId) {
        setCurrentChatId(null);
        setMessages([]);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to delete chat");
    }
  },

  sendMessage: async (content: string) => {
    const state = get();
    const {
      currentChatId,
      setStreaming,
      setError,
      addMessage,
      appendToLastMessage,
      setCurrentWorkflow,
      createChat,
    } = state;

    // Create chat if none exists
    let chatId = currentChatId;
    if (!chatId) {
      try {
        chatId = await createChat(content.slice(0, 50) + (content.length > 50 ? "..." : ""));
      } catch {
        return;
      }
    }

    // Add user message placeholder (will be confirmed by server)
    const userMessage: Message = {
      id: `temp-user-${Date.now()}`,
      chatId,
      role: "user",
      content,
      createdAt: new Date(),
    };
    addMessage(userMessage);

    // Add assistant message placeholder
    const assistantMessage: Message = {
      id: `temp-assistant-${Date.now()}`,
      chatId,
      role: "assistant",
      content: "",
      createdAt: new Date(),
    };
    addMessage(assistantMessage);

    setStreaming(true);
    setError(null);
    setCurrentWorkflow(null);

    try {
      await api.sendMessageStream(chatId, content, {
        onMessageStart: (type, messageId) => {
          if (type === "user" && messageId) {
            // Update temp user message with real ID
            get().updateMessage(userMessage.id, { id: messageId });
          }
        },
        onContentDelta: (chunk) => {
          appendToLastMessage(chunk);
        },
        onMessageEnd: (messageId, hasWorkflow) => {
          // Update temp assistant message with real ID
          get().updateMessage(assistantMessage.id, { id: messageId });
          if (!hasWorkflow) {
            setStreaming(false);
          }
        },
        onWorkflowCreated: (workflow) => {
          setCurrentWorkflow(workflow);
          // Update message with workflow ID
          get().updateMessage(assistantMessage.id, { workflowId: workflow.id });
          setStreaming(false);
        },
        onError: (error) => {
          setError(error);
          setStreaming(false);
        },
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to send message");
      appendToLastMessage("\n\nSorry, an error occurred. Please try again.");
      setStreaming(false);
    }
  },
}));
