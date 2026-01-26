from doctr.io import DocumentFile
from doctr.models import ocr_predictor

# Load once (CPU-safe)
model = ocr_predictor(
    det_arch="db_resnet50",
    reco_arch="crnn_vgg16_bn",
    pretrained=True
)

def run_doctr_ocr(image_path: str) -> str:
    doc = DocumentFile.from_images(image_path)
    result = model(doc)

    lines = []
    for page in result.pages:
        for block in page.blocks:
            for line in block.lines:
                words = [w.value for w in line.words]
                lines.append(" ".join(words))

    return "\n".join(lines)
