import modules.scripts as scripts
import gradio as gr

from modules import sd_samplers, shared
from modules.processing import Processed, process_images
from pathlib import Path
import pathlib
import os
import os.path


def add_to_prompt(prompt, prompt_to_append, prompt_seperator, replace_underscore):
	if replace_underscore:
		prompt_append = ''.join(prompt_to_append).replace("_", " ")
	else:
		prompt_append = ''.join(prompt_to_append)
		
	if prompt_seperator == "none":
		return prompt + prompt_append if prompt != '' else prompt_append
	elif prompt_seperator == "space":
		return prompt + " " + prompt_append if prompt != '' else prompt_append
	elif prompt_seperator == "pipe":
		return prompt + "|" + prompt_append if prompt != '' else prompt_append
	else:
		return prompt + ", " + prompt_append if prompt != '' else prompt_append

def add_to_negativeprompt(prompt, prompt_to_append, prompt_seperator, replace_underscore):
	prompt_append = ''.join(prompt_to_append)
	if prompt_seperator == "none":
		return prompt + prompt_append if prompt != '' else prompt_append
	elif prompt_seperator == "space":
		return prompt + " " + prompt_append if prompt != '' else prompt_append
	elif prompt_seperator == "pipe":
		return prompt + "|" + prompt_append if prompt != '' else prompt_append
	else:
		return prompt + ", " + prompt_append if prompt != '' else prompt_append


def load_text(list_to_find):
	promptgen_dict = {}
	for result in Path('scripts/wildcards').rglob(list_to_find):
		found_result = pathlib.Path(result)
	if os.path.exists(found_result):
		with open(found_result, "r", encoding="utf8") as file:
			count = 1
			for line in file:
				#value = line.split()
				promptgen_dict[int(count)] = line.strip()
				#promptgen_dict[int(count)] = value
				count += 1
		return gr.Dropdown.update(choices=[v for k, v in promptgen_dict.items()])
		#return promptgen_dict

def list_wildcard_texts():
	if os.path.exists('scripts/wildcards'):
		wild_dict = {}
		count = 1
		for path in Path('scripts/wildcards').rglob('*.txt'):
			value = path.name
			wild_dict[int(count)] = value
			count += 1
		return wild_dict
		
#prompt_adjectives = load_promptgen_text('scripts/wildcards/adjective.txt')
class Script(scripts.Script):
	def title(self):
		return "Prompt Helper"

	def ui(self, is_img2img):
		with gr.Row():
			genprompt = gr.Textbox(label='Prompt', show_label=False, lines=3, placeholder="Prompt")
		with gr.Row():
			negprompt = gr.Textbox(label='Negative Prompt', show_label=False, lines=2, placeholder="Negative Prompt")
		with gr.Row():
			prompt_seperator = gr.Radio(label='Seperator to use', show_label=False, choices=["comma","space", "pipe", "none"], value="comma", type="value")		
		with gr.Row():
			wildcard_file_list = list_wildcard_texts()
			wildcard_list = gr.Dropdown(label="Wildcard Files", elem_id="wildcard_index",choices=[v for k, v in wildcard_file_list.items()], value=next(iter(wildcard_file_list.keys())), interactive=True)
		with gr.Row():
			text_list = gr.Dropdown(label="Items inside selected text file", elem_id="text_index")
		with gr.Row():
			append_prompt = gr.Button('Add to prompt')
			append_negativeprompt = gr.Button('Add to negative prompt')
			replace_underscore = gr.Checkbox(label='Replace underscores with spaces.', value=False)

		append_prompt.click(
			fn=add_to_prompt,
			inputs=[
				genprompt,
				text_list,
				prompt_seperator,
				replace_underscore,
			],
			outputs=[
				genprompt,
			]
		)
		append_negativeprompt.click(
			fn=add_to_negativeprompt,
			inputs=[
				negprompt,
				text_list,
				prompt_seperator,
				replace_underscore,
			],
			outputs=[
				negprompt,
			]
		)
		wildcard_list.change(
			fn=load_text,
			inputs=[
			wildcard_list,
			],
			outputs=[
			text_list,
			]
		)
		return [genprompt, negprompt, wildcard_list, text_list, prompt_seperator, append_prompt, append_negativeprompt, replace_underscore]

	def run(self, p, prompt, negprompt, wildcard_list, text_list, prompt_seperator, append_prompt, append_negativeprompt, replace_underscore):
		images = []
		p.prompt = prompt
		p.negative_prompt = negprompt
		proc = process_images(p)
		images += proc.images

		return Processed(p, images, p.seed, proc.info)