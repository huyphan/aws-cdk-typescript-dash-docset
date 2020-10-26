wget -nH -np -P tmp --recursive https://docs.aws.amazon.com/cdk/api/latest/typescript/index.html
wget -nH -np -P tmp --recursive https://docs.aws.amazon.com/cdk/api/latest/typescript/api/toc.html
mkdir -p aws-cdk-ts.docset/Contents/Resources/Documents
cp resources/Info.plist aws-cdk-ts.docset/Contents/Info.plist
cp resources/docSet.dsidx aws-cdk-ts.docset/Contents/Resources/docSet.dsidx
cp -r tmp/cdk/api/latest/typescript/* aws-cdk-ts.docset/Contents/Resources/Documents
python gen_docset.py
