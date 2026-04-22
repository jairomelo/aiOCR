---
model: deepseek-OCR
runtime: T4 GPU
RAM: 9.4 / 12.7 GB
GPU RAM: 5.6 / 15 GB
Disk: 49.6 / 112.6 GB
prompt: Convert the document to text and be as close to the original text as possible (including any typos, print errors, keeping the original grammar and spelling).
time-reasoning: 60s
attachement: images/pineda1/pineda1_page_4.png
image size:  (1125, 1794)
valid image tokens:  160
output texts tokens (valid):  744
compression ratio:  4.65
---

The attention mask and the pad token id were not set. As a consequence, you may observe unexpected behavior. Please pass your input's `attention_mask` to obtain reliable results.
Setting `pad_token_id` to `eos_token_id`:None for open-end generation.
=====================
BASE:  torch.Size([1, 256, 1280])
NO PATCHES
=====================
1-4-<|end_of_line|>1-4-<|end_of_line|>1-4-<|md_start_of_line|>1-4-<|md_end_of_line|>
<|ref|>text<|/ref|><|det|>[[78, 70, 830, 151]]<|/det|>
puede aguardar la sentencia que ha de entregarle inocente. Escúpenle en el rostro, le abofetean, le azotan con varas hasta dejar descubiertas las venas i los huesos: el cuerpo de la víctima no es mas que una llaga de los pies a la cabeza. 

<|ref|>text<|/ref|><|det|>[[78, 153, 830, 313]]<|/det|>
A la crueldad se junta una mofa insultante. Como el tigre que juega con su presa antes de devorarla, así aquel pueblo bárbaro ultraja al manso cordero ántes de vértet su sangre. Le visten una tónica de escarnio: le ponen en la mano una caña á guisa de ceetro i en la cabeza una corona de espinas en señal de diadema: luego vendándole los ojos doblan la rodilla, le dan fuertes bofetadas en el rostro i le dicen: Dios te guarde, rei de los judíos. 

<|ref|>text<|/ref|><|det|>[[78, 316, 830, 590]]<|/det|>
¡I este justo era el bienhechor público de la nacion! Entre aquel pueblo de vérdugos no se hallaria uno que no hubiese esperimentado los saludables efectos de la poderosa bondad de él en su persona o en la de los suyos. Purificó á los leprosos, restituyó la vista á los ciegos i el oído á los sordos, libró á los endemoniados, resucitó los muertos, á todos hizo bien i á ninguno mal. Miéntras le conclucan como un vaso de tierra, se mantiene él sereno i lleno de dignidad. Semejante al tierno cordero que es conducido en silencio al matadero, así él se deja llevar al suplicio sin abrir la boca. Conjúranle en el nombre de Dios que hable, i él responde con mansedumbre i verdad. Sus palabras se imputan á crimen, i un bofeton nas es el premio de su obediencia. 

<|ref|>text<|/ref|><|det|>[[78, 594, 830, 810]]<|/det|>
El justo le recibe i calla. Su resignacion exaspera á los persiguidores, cuyas vociferaciones van en aumento haciendo resonar como un trueno los ecos de la ciudad deicida: Que le erucifiquen: que le crucifiquen; i le llevan brutalmente á empellones ante el juez que puede entre- garles la cabeza del inocente. Este juez es un estranjero un ambicioso, un cobarde; sin embargo le domina la inocencia del acusado i la proclama diciendo: «¡Qué mal ha hecho!--Si no fuera culpable, no te le hubiéramos entregado.--Pues ¡qué mal ha hecho!--Aspira á reinar, i nosotros no queremos que reine sobre nosotros [1].»
==================================================
image size:  (1125, 1794)
valid image tokens:  160
output texts tokens (valid):  744
compression ratio:  4.65
==================================================
===============save results:===============
image: 0it [00:00, ?it/s]
other: 100%|██████████| 4/4 [00:00<00:00, 47259.76it/s]