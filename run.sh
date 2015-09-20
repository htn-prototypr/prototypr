mkdir -p image_queue

FILES="$(gsutil ls gs://prototypr-images)"

chosen_file="image_queue/$(ls image_queue/ | sort -n | head -1)"
curr_dir="$(pwd)"
echo $chosen_file

if [ "$chosen_file" == "" ]; then
    gsutil cp gs://prototypr-images/* image_queue/
    gsutil mv gs://prototypr-images/* gs://prototypr-images-processed/
    chosen_file="image_queue/$(ls image_queue/ | sort -n | head -1)"
    echo $chosen_file

    if [ "$chosen_file" == "" ]; then
        echo "No files in Cloud Storage or local, exiting application!";
        exit 1;
    fi
fi

# now call image processor application
cd reactify
python img_proc.py $curr_dir/$chosen_file

# now call json to react
node json2react.js example.json

if [ $? != 0 ]; then
    echo "Converting JSON to React JS code failed!"
    exit 1;
fi

python reactify.py

echo "Prototyped image: $chosen_file!"
