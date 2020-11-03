mkdir -p aws-cdk-ts.docset/Contents/Resources/Documents/api
cp resources/Info.plist aws-cdk-ts.docset/Contents/Info.plist
cp resources/docSet.dsidx aws-cdk-ts.docset/Contents/Resources/docSet.dsidx

wget -nH -np -P tmp --recursive https://docs.aws.amazon.com/cdk/api/latest/typescript/index.html
wget -nH -np -P tmp --recursive https://docs.aws.amazon.com/cdk/api/latest/typescript/api/toc.html
wget https://docs.aws.amazon.com/cdk/api/latest/docs/aws-construct-library.html -O tmp/aws-construct-library.html

 cp -r tmp/cdk/api/latest/typescript/{fonts,styles} aws-cdk-ts.docset/Contents/Resources/Documents

 # python gen_docset.py
