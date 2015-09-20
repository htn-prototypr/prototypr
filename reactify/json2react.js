var fs = require('fs');

var layer_colours = [ "#DDDDDD", "#BBBBBB" ];

function get_json (callback) {
    fs.readFile('example.json', function (err, data) {
        // check if read file succeeds
        if (err) {
            callback(false, err);
        }

        var json = null;
        
        // build JSON object
        try {
            json = JSON.parse(data);
        } catch (e) {
            callback(false, e);
        }

        callback(true, json);
    });
}

function build_tabs_string (level) {
    var tabs_string = "";
    for (var i = 0; i < level; i++) tabs_string += "    ";
    return tabs_string;
}

function add_stylesheet_entry (Stylesheet, view, level) {
    Stylesheet.push(view.id + ": {");
    var style = view.style;
    for (var i in style) {
        if (typeof style[i] === 'number')
            Stylesheet.push("    " + i + ": " + style[i] + ",");
        else
            Stylesheet.push("    " + i + ": '" + style[i] + "',");
    }

    // add default styles for a text view
    if (view.type === 'text_view') {
        Stylesheet.push("    fontSize: 12,");
        Stylesheet.push("    textAlign: 'center',");
    }

    // default background colours so we can distinguish between different elements in the UI
    Stylesheet.push("    backgroundColor: '" + layer_colours[level % 2] + "'");
    Stylesheet.push("},");
}

function recurse_build_jsx_and_stylesheet (JSXArray, Stylesheet, view_array, level, generator) {
    for (var i in view_array) {
        var closing = false;
        var view = view_array[i];
        JSXArray.push(build_tabs_string(level) + generator.get_xml_tag(view.type, view.id, closing));
        add_stylesheet_entry(Stylesheet, view, level);
        recurse_build_jsx_and_stylesheet (JSXArray, Stylesheet, view.children, level + 1, generator);
        closing = true;
        JSXArray.push(build_tabs_string(level) + generator.get_xml_tag(view.type, view.id, closing));
    }
}

function build_jsx_and_stylesheet (view_json, callback, generator) {
    var JSXArray = [];
    var Stylesheet = [];

    Stylesheet.push("_root: {},");
    
    JSXArray.push("<View style={styles._root}>");
    recurse_build_jsx_and_stylesheet(JSXArray, Stylesheet, view_json["root"]["children"], 1, generator);
    JSXArray.push("</View>");
    callback(JSXArray, Stylesheet);
}

function customCreateWriteStream (fs, filePath) {
    var writable = fs.createWriteStream(filePath, { flags: 'a' });
    writable.on('error', function () {
        process.exit(1);
    });
    return writable;
}

function generate_react(generator) {
    var filePath = './js/test/index.android.js';
    var writable = customCreateWriteStream(fs, filePath);
    var readable = fs.createReadStream('react_template/android_template_1.js');
    readable.pipe(writable);
    writable.on('finish', function () {
        var writable = customCreateWriteStream(fs, filePath);
        var readable = fs.createReadStream('react_template/android_template_2.js');
        get_json(function (success, view_json) {
            if (success) {
                build_jsx_and_stylesheet(view_json, function (JSXArray, Stylesheet) {
                    for (var i in JSXArray) {
                        writable.write(JSXArray[i]);
                        writable.write("\n");
                    }
                    readable.pipe(writable);
                    writable.on('finish', function () {
                        var writable = customCreateWriteStream(fs, filePath);
                        for (var i in Stylesheet) {
                            writable.write(Stylesheet[i]);
                            writable.write("\n");
                        }
                        var readable = fs.createReadStream('react_template/android_template_3.js');
                        readable.pipe(writable);
                        writable.on('finish', function () {
                            console.log("Conversion of JSON to React code succeeded!");
                            process.exit(0);
                        });
                    }); 
                }, generator);
            } else {
                process.exit(1);
            }
        });
    });
}

if (process.argv.length != 3) {
    console.error("Not the right number of parameters pass to json2react! Need 1 but got " + (process.argv.length - 2));
    process.exit(1);
}

file_path = "gen_json/" + process.argv[2];
fs.exists(file_path, function (exists) {
    if (!exists) {
        console.error("JSON file path passed to json2react does not exist!");
        process.exit(1);
    }
    var android_generator = require('./generators/android_generator');
    var ios_generator = require('./generators/ios_generator');
    generate_react(android_generator);
});
