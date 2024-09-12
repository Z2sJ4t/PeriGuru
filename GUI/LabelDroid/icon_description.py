import pickle

import cv2
import torch
from torchvision import transforms

from GUI.LabelDroid.models.image_models import ResNetFeats
from GUI.LabelDroid.models.Transformer import Transformer
from GUI.LabelDroid.data_utils.Vocabulary import Vocabulary

def config_args():
	args = {}
	args["vocab_path"] = './third_party/LabelDroid/vocabulary/vocab.pkl'
	args["model_path"] = './third_party/LabelDroid/best_model.ckpt'
	args["caption_model"] = "transformer"
	args["max_tokens"] = 15
	args["img_fatures_size"] = 2048
	args["embed_size"] = 512
	args["num_layers"] = 3
	args["drop_prob_lm"] = 0.1
	args["ff_size"] = 2048
	args["use_bn"] = False
	args["finetune_cnn"] = False
	args["att_size"] = 7
	args["batch_size"] = 4

	return args

def icon_description(images):
	args = config_args()

    # Device configuration
	device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

	# Load vocabulary 
	with open(args["vocab_path"], 'rb') as f:
		vocab = pickle.load(f)
	args["vocab_len"] = len(vocab)
	idx2word = vocab.idx2word

	# Load weights	
	checkpoint = torch.load(args["model_path"], map_location=device)
	encoder = ResNetFeats(args) 
	decoder = Transformer(args)

	decoder.load_state_dict(checkpoint['decoder_state_dict'])
	encoder.load_state_dict(checkpoint['encoder_state_dict'])
	decoder.to(device)
	encoder.to(device)
	decoder.eval()
	encoder.eval()

	# Processing images
	img_size = (224, 224)
	mean = [ 0.485, 0.456, 0.406 ]
	std  = [ 0.229, 0.224, 0.225 ]

	preds = []
	for img in images:
		# Convert to torch tensor 
		# and then add one dimension -> [1, 3, 244, 244]
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		img = cv2.resize(img, img_size)
		img = torch.from_numpy(img).permute(2, 0, 1).float() / 255.0
		for channel, m, s in zip(range(3), mean, std):
			img[channel] = (img[channel] - m) / s
		img = img.unsqueeze(0).to(device)

		features = encoder(img)
		sentence_ids = decoder.evaluate(features, max_len=args["max_tokens"]).numpy()

		# Convert word_ids to words
		for j in range(min(len(sentence_ids), args["batch_size"])):
			sampled_caption = []
			word_raw_id = []
			
			unk_flag = False

			for word_id in sentence_ids[j]:
				word = idx2word[word_id]
				word_raw_id.append(word_id)
				if(word == '<end>'):
					break
				if(word == '<pad>' or word == '<unk>'):
					unk_flag = True
					break
				sampled_caption.append(word)

			if(unk_flag):
				sentence = '<unk>'
			else:
				sentence = ' '.join(sampled_caption[1:])
			word_raw_id = word_raw_id[1:]
			word_raw_id = [str(raw) for raw in word_raw_id]
			# Remove unrecognized descriptions
			preds.append(sentence)
	
	return preds