---
model: deepseek-OCR
runtime: T4 GPU
RAM: 9.4 / 12.7 GB
GPU RAM: 5.6 / 15 GB
Disk: 49.6 / 112.6 GB
prompt: Convert the document to text and be as close to the original text as possible (including any typos, print errors, keeping the original grammar and spelling).
time-reasoning: 42s
attachement: images/pineda1/pineda1_page_3.png
image size:  (1168, 1811)
valid image tokens:  165
output texts tokens (valid):  387
compression ratio:  2.35
---

The attention mask and the pad token id were not set. As a consequence, you may observe unexpected behavior. Please pass your input's `attention_mask` to obtain reliable results.
Setting `pad_token_id` to `eos_token_id`:None for open-end generation.
The attention mask is not set and cannot be inferred from input because pad token is same as eos token. As a consequence, you may observe unexpected behavior. Please pass your input's `attention_mask` to obtain reliable results.
The `seen_tokens` attribute is deprecated and will be removed in v4.41. Use the `cache_position` model input instead.
`get_max_cache()` is deprecated for all Cache classes. Use `get_max_cache_shape()` instead. Calling `get_max_cache()` will raise error from v4.48
The attention layers in this model are transitioning from computing the RoPE embeddings internally through `position_ids` (2D tensor with the indexes of the tokens), to using externally computed `position_embeddings` (Tuple of tensors, containing cos and sin). In v4.46 `position_ids` will be removed and `position_embeddings` will be mandatory.
=====================
BASE:  torch.Size([1, 256, 1280])
NO PATCHES
=====================
0.0000000000000000000000000000000000000000000000000000000000000
<|ref|>text<|/ref|><|det|>[[222, 199, 830, 240]]<|/det|>
¿A DONDE VAMOS A PARAR? 

<|ref|>text<|/ref|><|det|>[[163, 363, 904, 431]]<|/det|>
A la familia i á cada uno de sus miembros, á los padres, á los hijos, á los jóvenes, á los ancianos. 

<|ref|>text<|/ref|><|det|>[[300, 473, 781, 503]]<|/det|>
¿Qué daño os ha hecho? 

<|ref|>text<|/ref|><|det|>[[520, 533, 560, 552]]<|/det|>
I. 

<|ref|>text<|/ref|><|det|>[[163, 574, 908, 860]]<|/det|>
A CERCABASE la hora fatal: Jas potestades de las tinieblas se habían desenfrenado; i hé aquí que todo un pueblo dominado de un espíritu de furor i de vértigo se apodera del Juzro. Eos propios discípulos de este, educados en su escuela, alimentados con su pan, colmados de caricias, sus discípulos que acaban de jurarle una fidelidad á toda prueba, le abandonan i le niegan: uno de ellos le ha vendido. Atado como un malhechor es conducido de tribunal en tribunal por las calles de una gran ciudad. Hombres, mujeres, niños, majistrados, ancianos con los cabellos blancos, todos han acudido i forman la tumultaria comitiva. De entre aquella multitud horrible como un hombre ébrio i ajitada como un mar borrascoso adén incesantemente gritos de muerte. El odio impaciente no
==================================================
image size:  (1168, 1811)
valid image tokens:  165
output texts tokens (valid):  387
compression ratio:  2.35
==================================================
===============save results:===============
image: 0it [00:00, ?it/s]
other: 100%|██████████| 5/5 [00:00<00:00, 64329.82it/s]