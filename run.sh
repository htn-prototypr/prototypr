mkdir -p image_queue

FILES="$(gsutil ls gs://prototypr-images)"

gsutil cp gs://prototypr-images/* image_queue/
gsutil mv gs://prototypr-images/* gs://prototypr-images-processed/

# now call image processor application

# now call json to react
cd reactify
node json2react.js
python reactify.py
