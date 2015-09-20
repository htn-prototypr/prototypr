mkdir -p image_queue

FILES="$(gsutil ls gs://prototypr-images)"

chosen_file="image_queue/$(ls image_queue/ | sort -n | head -1)"

if [ ! $chosen_file ]; then
    gsutil cp gs://prototypr-images/* image_queue/
    gsutil mv gs://prototypr-images/* gs://prototypr-images-processed/
    chosen_file="$(ls image_queue/ | sort -n | head -1)"

    if [ ! $chosen_file ]; then
        echo "No files in Cloud Storage or local, exiting application!";
        return 0;
    fi
fi

# now call image processor application

# now call json to react
cd reactify
node json2react.js example.json

if [ $? != 0 ]; then
    echo "Converting JSON to React JS code failed!"
    return 0;
fi

python reactify.py

echo "Prototyped image: $chosen_file!"
