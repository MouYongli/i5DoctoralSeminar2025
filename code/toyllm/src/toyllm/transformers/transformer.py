"""
Simple Transformer implementation from scratch using PyTorch.
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class MultiHeadAttention(nn.Module):
    """Multi-Head Self-Attention mechanism."""

    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % n_heads == 0, "d_model must be divisible by n_heads"

        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads

        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

        self.dropout = nn.Dropout(dropout)

    def scaled_dot_product_attention(
        self,
        Q: torch.Tensor,
        K: torch.Tensor,
        V: torch.Tensor,
        mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """
        Compute scaled dot-product attention.

        Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
        """
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, float("-inf"))

        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)

        return torch.matmul(attn_weights, V)

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        batch_size = query.size(0)

        # Linear projections and reshape to (batch, n_heads, seq_len, d_k)
        Q = self.W_q(query).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(key).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(value).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)

        # Apply attention
        attn_output = self.scaled_dot_product_attention(Q, K, V, mask)

        # Concatenate heads and project
        attn_output = (
            attn_output.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        )

        return self.W_o(attn_output)


class FeedForward(nn.Module):
    """Position-wise Feed-Forward Network."""

    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.fc1 = nn.Linear(d_model, d_ff)
        self.fc2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc2(self.dropout(F.gelu(self.fc1(x))))


class PositionalEncoding(nn.Module):
    """Sinusoidal Positional Encoding."""

    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)  # (1, max_len, d_model)

        self.register_buffer("pe", pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.pe[:, : x.size(1)]
        return self.dropout(x)


class TransformerEncoderBlock(nn.Module):
    """Single Transformer Encoder Block."""

    def __init__(self, d_model: int, n_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, n_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(
        self, x: torch.Tensor, mask: torch.Tensor | None = None
    ) -> torch.Tensor:
        # Self-attention with residual connection and layer norm
        attn_output = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))

        # Feed-forward with residual connection and layer norm
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_output))

        return x


class TransformerDecoderBlock(nn.Module):
    """Single Transformer Decoder Block."""

    def __init__(self, d_model: int, n_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.self_attention = MultiHeadAttention(d_model, n_heads, dropout)
        self.cross_attention = MultiHeadAttention(d_model, n_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,
        encoder_output: torch.Tensor,
        src_mask: torch.Tensor | None = None,
        tgt_mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        # Masked self-attention
        attn_output = self.self_attention(x, x, x, tgt_mask)
        x = self.norm1(x + self.dropout(attn_output))

        # Cross-attention with encoder output
        attn_output = self.cross_attention(x, encoder_output, encoder_output, src_mask)
        x = self.norm2(x + self.dropout(attn_output))

        # Feed-forward
        ff_output = self.feed_forward(x)
        x = self.norm3(x + self.dropout(ff_output))

        return x


class Transformer(nn.Module):
    """Complete Transformer model."""

    def __init__(
        self,
        vocab_size: int,
        d_model: int = 512,
        n_heads: int = 8,
        n_encoder_layers: int = 6,
        n_decoder_layers: int = 6,
        d_ff: int = 2048,
        max_len: int = 5000,
        dropout: float = 0.1,
    ):
        super().__init__()

        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_len, dropout)

        self.encoder_layers = nn.ModuleList(
            [
                TransformerEncoderBlock(d_model, n_heads, d_ff, dropout)
                for _ in range(n_encoder_layers)
            ]
        )

        self.decoder_layers = nn.ModuleList(
            [
                TransformerDecoderBlock(d_model, n_heads, d_ff, dropout)
                for _ in range(n_decoder_layers)
            ]
        )

        self.fc_out = nn.Linear(d_model, vocab_size)

    def generate_causal_mask(self, size: int, device: torch.device) -> torch.Tensor:
        """Generate causal mask for decoder self-attention."""
        mask = torch.triu(torch.ones(size, size, device=device), diagonal=1)
        return mask == 0

    def encode(
        self, src: torch.Tensor, src_mask: torch.Tensor | None = None
    ) -> torch.Tensor:
        x = self.embedding(src) * math.sqrt(self.d_model)
        x = self.pos_encoding(x)

        for layer in self.encoder_layers:
            x = layer(x, src_mask)

        return x

    def decode(
        self,
        tgt: torch.Tensor,
        encoder_output: torch.Tensor,
        src_mask: torch.Tensor | None = None,
        tgt_mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        x = self.embedding(tgt) * math.sqrt(self.d_model)
        x = self.pos_encoding(x)

        for layer in self.decoder_layers:
            x = layer(x, encoder_output, src_mask, tgt_mask)

        return x

    def forward(
        self,
        src: torch.Tensor,
        tgt: torch.Tensor,
        src_mask: torch.Tensor | None = None,
        tgt_mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        if tgt_mask is None:
            tgt_mask = self.generate_causal_mask(tgt.size(1), tgt.device)

        encoder_output = self.encode(src, src_mask)
        decoder_output = self.decode(tgt, encoder_output, src_mask, tgt_mask)

        return self.fc_out(decoder_output)


if __name__ == "__main__":
    # Demo usage
    vocab_size = 10000
    batch_size = 2
    src_len = 10
    tgt_len = 8

    model = Transformer(vocab_size=vocab_size, d_model=256, n_heads=8, d_ff=1024)

    src = torch.randint(0, vocab_size, (batch_size, src_len))
    tgt = torch.randint(0, vocab_size, (batch_size, tgt_len))

    output = model(src, tgt)
    print(f"Input shape: src={src.shape}, tgt={tgt.shape}")
    print(f"Output shape: {output.shape}")  # (batch_size, tgt_len, vocab_size)