---
model: deepseek-OCR
runtime: T4 GPU
RAM: 9.4 / 12.7 GB
GPU RAM: 5.6 / 15 GB
Disk: 49.6 / 112.6 GB
prompt: Convert the document to text and be as close to the original text as possible (including any typos, print errors, keeping the original grammar and spelling).
time-reasoning: ?
attachement: images/pineda1/pineda1_page_1.png
image size:  (1139, 1794)
valid image tokens:  162
output texts tokens (valid):  186
compression ratio:  1.15
---

The attention mask and the pad token id were not set. As a consequence, you may observe unexpected behavior. Please pass your input's `attention_mask` to obtain reliable results.
Setting `pad_token_id` to `eos_token_id`:None for open-end generation.
=====================
BASE:  torch.Size([1, 256, 1280])
NO PATCHES
=====================
2
<|ref|>text<|/ref|><|det|>[[100, 0, 900, 160]]<|/det|>
¿A DONDE VAMOS A PARAR?
O JEAADA 

SOBRE LAS TENDENCIAS DE LA ÉPOCA ACTUAL:

FOR 

El presidente S. Gaume, 

VICARIO JENERAL DE LA DIÓCESIS DE NEVERS, CABALLERO 
DE LA ORDEN DE S. SILVESTRE, INDIVIDUO DE LA ACADEMIA 
DE LA RELIÓN CATÓLICA EN ROMA ETC. 

Videte, vigilate et orate. 
Ved, velad i orad. 
S. MARC. XII, 33. 

BOGOTA. 

REIMP. EN LA DE TORRES AMAYA POR CARLOS LOPEZ. 

1852.
==================================================
image size:  (1139, 1794)
valid image tokens:  162
output texts tokens (valid):  186
compression ratio:  1.15
==================================================
===============save results:===============
image: 0it [00:00, ?it/s]
other: 100%|██████████| 1/1 [00:00<00:00, 14364.05it/s]