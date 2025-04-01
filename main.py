from tercen.client import context as ctx
import numpy as np
import pandas as pd
import json
import os
from PIL import Image

tercenCtx = ctx.TercenContext(
    workflowId="241160841cead65995c0c45d0a011ce8",
    stepId="43f1bc61-3638-41e0-8b05-f5a2c888ea38",
    username="admin", # if using the local Tercen instance
    password="admin", # if using the local Tercen instance
    serviceUri = "http://127.0.0.1:5402/" # if using the local Tercen instance 
)

imageDocumentId = tercenCtx.cubeQuery.toJson()["relation"]["relation"]["inMemoryTable"]["columns"][0]["values"][0]
print(imageDocumentId)

aliasId = tercenCtx.document_alias_to_id(imageDocumentId, "documentId")


httpResponse = tercenCtx.client.fileService.download(aliasId)

with open("image.bmp", "wb") as f:
    f.write(httpResponse.read())

def bmp_to_dataset(image_path):
    print("Loading image from: ", image_path)
    # Open the BMP image
    img = Image.open(image_path)
    img = img.convert('RGB')  # Ensure RGB format
    
    width, height = img.size

    #res is an array of 3 columns [color_code, x, y, .ci, .ri] and width*height rows
    res = np.zeros((width*height, 5), dtype=int)

    for y in range(height):
            for x in range(width):
                r, g, b = img.getpixel((x, y))
                color_code = (r << 16) + (g << 8) + b
                res[y*width + x] = [color_code, x, y, x, y]

    return res

df = bmp_to_dataset("image.bmp")

#delete the image file
os.remove("image.bmp")

df = pd.DataFrame(df, columns=["color_code", "x", "y", ".ci", ".ri"])
df = df.astype({"color_code": "int32", "x": "int32", "y": "int32", ".ci": "int32", ".ri": "int32"})

df = tercenCtx.add_namespace(df) 
tercenCtx.save(df)
