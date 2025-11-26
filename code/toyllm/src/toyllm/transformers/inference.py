import torch
from torch import nn
from transformers.generation_utils import GenerationMixin

# Greedy
model.generate(input_ids, max_length=50)

# Beam Search
model.generate(input_ids, num_beams=5)

# Sampling
model.generate(input_ids, do_sample=True, top_k=50, top_p=0.95, temperature=0.7)

# Contrastive Search
model.generate(input_ids, penalty_alpha=0.6, top_k=4)