from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

mtcnn = MTCNN(keep_all=False, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)


@app.get("/")
def health():
    return {"status": "Facenet AI Service Running"}


@app.post("/extract-embedding")
async def extract_embedding(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        np_arr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        face = mtcnn(img_rgb)

        if face is None:
            raise HTTPException(status_code=400, detail="Face not detected")

        face = face.unsqueeze(0).to(device)

        embedding = resnet(face).detach().cpu().numpy()[0]

        # L2 normalize
        embedding = embedding / np.linalg.norm(embedding)

        return {
            "embedding": embedding.tolist(),
            "dimensions": len(embedding)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))