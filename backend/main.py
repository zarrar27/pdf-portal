"""PDF Portal API — version 2: lists PDFs in S3 and hands out presigned URLs."""

import os

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

S3_BUCKET = os.environ["S3_BUCKET"]
S3_PREFIX = os.getenv("S3_PREFIX", "pdfs/")
URL_EXPIRY_SECONDS = int(os.getenv("URL_EXPIRY_SECONDS", "300"))
AWS_REGION = os.environ["AWS_REGION"]

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    endpoint_url=f"https://s3.{AWS_REGION}.amazonaws.com",
    config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
)

app = FastAPI(title="PDF Portal API", version="0.2.0")


@app.get("/health")
def health():
    """Health check, used by load balancers to see if the app is alive."""
    return {"status": "ok"}


@app.get("/api/pdfs")
def list_pdfs():
    """List every PDF under S3_PREFIX in the bucket."""
    files = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=S3_PREFIX):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.lower().endswith(".pdf"):
                files.append({
                    "name": key[len(S3_PREFIX):],
                    "size_bytes": obj["Size"],
                    "last_modified": obj["LastModified"].isoformat(),
                })
    files.sort(key=lambda f: f["name"])
    return {"count": len(files), "files": files}


@app.get("/api/pdfs/{filename}")
def get_pdf(filename: str, download: bool = False):
    """Redirect to a short-lived presigned S3 URL for one PDF."""
    if "/" in filename or "\\" in filename or not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file name")

    key = S3_PREFIX + filename
    try:
        s3.head_object(Bucket=S3_BUCKET, Key=key)
    except ClientError as err:
        if err.response["Error"]["Code"] in ("404", "NoSuchKey"):
            raise HTTPException(status_code=404, detail="PDF not found")
        raise

    disposition = "attachment" if download else "inline"
    url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": key,
            "ResponseContentType": "application/pdf",
            "ResponseContentDisposition": f'{disposition}; filename="{filename}"',
        },
        ExpiresIn=URL_EXPIRY_SECONDS,
    )
    return RedirectResponse(url, status_code=307)