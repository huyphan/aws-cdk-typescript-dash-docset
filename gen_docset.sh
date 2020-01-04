wget -nH -np -P tmp --recursive https://docs.aws.amazon.com/cdk/api/latest/typescript/index.html
wget -nH -np -P tmp --recursive https://docs.aws.amazon.com/cdk/api/latest/typescript/api/toc.html
cp -r tmp/cdk/api/latest/typescript/* aws-cdk.docset/Contents/Resources/Documents
python gen_docset.py
