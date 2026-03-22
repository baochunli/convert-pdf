import pathlib
import shutil
import opendataloader_pdf

src = pathlib.Path("jar/opendataloader-pdf-cli.jar")
dst = pathlib.Path(opendataloader_pdf.__file__).resolve().parent / "jar" / "opendataloader-pdf-cli.jar"
dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(src, dst)
print(f"Copied {src} -> {dst}")
