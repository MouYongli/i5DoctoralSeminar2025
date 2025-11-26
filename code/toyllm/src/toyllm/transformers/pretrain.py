"""
Minimal DeepSpeed pretraining demo for a tiny causal Transformer.

This is intentionally small: it uses synthetic token data to showcase the pieces
needed for large-scale pretraining (model, optimizer, ZeRO config, and a loop).

Usage (after installing deepspeed):
    uv run --with deepspeed python -m toyllm.transformers.pretrain --train-steps 10
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

try:
    import deepspeed
except ImportError as exc:  # pragma: no cover - demo dependency
    raise SystemExit(
        "DeepSpeed is required for this demo. Install with `pip install deepspeed`."
    ) from exc

from .transformer import PositionalEncoding


class TinyCausalLM(nn.Module):
    """Small Transformer encoder stack used as a causal LM."""

    def __init__(
        self,
        vocab_size: int,
        d_model: int = 256,
        n_heads: int = 4,
        n_layers: int = 4,
        d_ff: int = 1024,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.d_model = d_model

        self.embed = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_len=2048, dropout=dropout)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_ff,
            dropout=dropout,
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)

    def _causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        mask = torch.triu(torch.ones(seq_len, seq_len, device=device), diagonal=1)
        mask = mask.masked_fill(mask == 1, float("-inf"))
        return mask

    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        # tokens: (batch, seq_len)
        x = self.embed(tokens) * math.sqrt(self.d_model)
        x = self.pos_encoding(x)
        mask = self._causal_mask(tokens.size(1), tokens.device)
        x = self.encoder(x, mask=mask)
        return self.lm_head(x)


class SyntheticTextDataset(Dataset[torch.Tensor]):
    """Generates random token sequences for quick, reproducible runs."""

    def __init__(self, num_samples: int, seq_len: int, vocab_size: int, seed: int = 0):
        generator = torch.Generator().manual_seed(seed)
        self.data = torch.randint(
            low=0,
            high=vocab_size,
            size=(num_samples, seq_len),
            dtype=torch.long,
            generator=generator,
        )

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> torch.Tensor:
        return self.data[idx]


@dataclass
class TrainConfig:
    vocab_size: int = 32000
    seq_len: int = 128
    batch_size: int = 4
    train_steps: int = 20
    lr: float = 5e-4
    grad_accum_steps: int = 1
    zero_stage: int = 1
    fp16: bool = False
    bf16: bool = True
    model_dim: int = 512
    heads: int = 8
    layers: int = 6
    ff_dim: int = 2048
    dropout: float = 0.1


def make_deepspeed_config(cfg: TrainConfig) -> dict[str, Any]:
    return {
        "train_batch_size": cfg.batch_size * cfg.grad_accum_steps,
        "gradient_accumulation_steps": cfg.grad_accum_steps,
        "optimizer": {
            "type": "AdamW",
            "params": {
                "lr": cfg.lr,
                "betas": [0.9, 0.95],
                "eps": 1e-8,
                "weight_decay": 0.01,
            },
        },
        "zero_optimization": {"stage": cfg.zero_stage},
        "fp16": {"enabled": cfg.fp16},
        "bf16": {"enabled": cfg.bf16},
    }


def parse_args() -> TrainConfig:
    parser = argparse.ArgumentParser(description="DeepSpeed pretraining demo.")
    parser.add_argument("--vocab-size", type=int, default=TrainConfig.vocab_size)
    parser.add_argument("--seq-len", type=int, default=TrainConfig.seq_len)
    parser.add_argument("--batch-size", type=int, default=TrainConfig.batch_size)
    parser.add_argument("--train-steps", type=int, default=TrainConfig.train_steps)
    parser.add_argument("--lr", type=float, default=TrainConfig.lr)
    parser.add_argument("--grad-accum-steps", type=int, default=TrainConfig.grad_accum_steps)
    parser.add_argument("--zero-stage", type=int, default=TrainConfig.zero_stage)
    parser.add_argument("--fp16", action="store_true", default=TrainConfig.fp16)
    parser.add_argument("--no-bf16", action="store_true", help="Disable bfloat16.")
    parser.add_argument("--model-dim", type=int, default=TrainConfig.model_dim)
    parser.add_argument("--heads", type=int, default=TrainConfig.heads)
    parser.add_argument("--layers", type=int, default=TrainConfig.layers)
    parser.add_argument("--ff-dim", type=int, default=TrainConfig.ff_dim)
    parser.add_argument("--dropout", type=float, default=TrainConfig.dropout)
    args = parser.parse_args()

    return TrainConfig(
        vocab_size=args.vocab_size,
        seq_len=args.seq_len,
        batch_size=args.batch_size,
        train_steps=args.train_steps,
        lr=args.lr,
        grad_accum_steps=args.grad_accum_steps,
        zero_stage=args.zero_stage,
        fp16=args.fp16,
        bf16=not args.no_bf16,
        model_dim=args.model_dim,
        heads=args.heads,
        layers=args.layers,
        ff_dim=args.ff_dim,
        dropout=args.dropout,
    )


def train(cfg: TrainConfig) -> None:
    torch.manual_seed(0)

    model = TinyCausalLM(
        vocab_size=cfg.vocab_size,
        d_model=cfg.model_dim,
        n_heads=cfg.heads,
        n_layers=cfg.layers,
        d_ff=cfg.ff_dim,
        dropout=cfg.dropout,
    )

    ds_config = make_deepspeed_config(cfg)
    engine, _, _, _ = deepspeed.initialize(
        model=model,
        model_parameters=model.parameters(),
        config=ds_config,
    )

    dataset = SyntheticTextDataset(
        num_samples=cfg.train_steps * cfg.batch_size,
        seq_len=cfg.seq_len,
        vocab_size=cfg.vocab_size,
    )
    dataloader = DataLoader(
        dataset,
        batch_size=cfg.batch_size,
        shuffle=True,
        drop_last=True,
    )

    global_step = 0
    engine.train()
    for step, batch in enumerate(dataloader):
        if global_step >= cfg.train_steps:
            break

        batch = batch.to(engine.device)
        inputs = batch[:, :-1]
        labels = batch[:, 1:]

        logits = engine(inputs)
        logits = logits[:, :-1, :]
        loss = F.cross_entropy(
            logits.reshape(-1, cfg.vocab_size),
            labels.reshape(-1),
        )

        engine.backward(loss)
        engine.step()

        if engine.global_rank == 0 and step % 1 == 0:
            print(f"step {global_step:04d} | loss: {loss.item():.4f}")

        global_step += 1


def main() -> None:
    cfg = parse_args()
    train(cfg)


if __name__ == "__main__":
    main()
