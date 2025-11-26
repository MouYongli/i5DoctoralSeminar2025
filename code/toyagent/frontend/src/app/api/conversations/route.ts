import { NextRequest, NextResponse } from "next/server";

// Mock data store (in-memory)
const conversations = new Map<string, Conversation>();

interface Conversation {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  preview?: string;
}

export async function GET() {
  const list = Array.from(conversations.values()).sort(
    (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  );
  return NextResponse.json(list);
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const conversation: Conversation = {
    id: crypto.randomUUID(),
    title: body.title || "New Conversation",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    preview: body.preview,
  };
  conversations.set(conversation.id, conversation);
  return NextResponse.json(conversation, { status: 201 });
}
