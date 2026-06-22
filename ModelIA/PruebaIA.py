import os
import torch
import torch.nn as nn

from PIL import Image
from torchvision import transforms
from torchvision.models import mobilenet_v2

bas = os.path.dirname(os.path.abspath(__file__))
Ubic = os.path.join(bas,"cartoon_v3.pt")
checkpoint = torch.load(Ubic, map_location="cpu", weights_only=False)

classes = checkpoint["classes"]

print("Clases:")
print(classes)

base = mobilenet_v2(weights=None)

class CartoonClassifier(nn.Module):

	def __init__(self):
		super().__init__()
		self.features = base.features
		self.pool = nn.AdaptiveAvgPool2d(1)
		self.head = nn.Sequential(nn.Linear(1280,512), nn.ReLU(), nn.Dropout(0.3),nn.Linear(512,17))

	def forward(self,x):
		x = self.features(x)
		x = self.pool(x)
		x= torch.flatten(x,1)
		x = self.head(x)
		return x



model = CartoonClassifier()

model.load_state_dict(checkpoint["model_state_dict"])

model.eval()

transform = transforms.Compose([transforms.Resize((224,224)), transforms.ToTensor(), transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])])


def clasificar_img(ruta):
	imagen = Image.open(ruta).convert("RGB")
	tensor = transform(imagen).unsqueeze(0)

	with torch.no_grad():
		salida = model(tensor)
		probs = torch.softmax(salida,dim=1)
		idx = torch.argmax(probs,dim=1).item()
	
	categoria = classes[idx]
	confianza = probs[0][idx].item()*100
	
	return categoria, confianza
