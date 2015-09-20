var fs = require('fs');

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

function convert_to_xml_tags (type, id, closing) {
    if (!closing) {
        switch(type) {
            case 'container': 
                return "<View style={" + id + "}>";
            default:
                return false;
        }
    } else {
        switch(type) {
            case 'container':
                return "</View>";
            default:
                return false;
        }
    }
}

function add_stylesheet_entry (Stylesheet, view) {
    Stylesheet.push(view.id + ": {");
    var style = view.style;
    for (var i in style) {
        Stylesheet.push("    " + i + ": " + style[i] + ",");
    }
    Stylesheet.push("},");
}

function recurse_build_jsx_and_stylesheet (JSXArray, Stylesheet, view_array) {
    for (var i in view_array) {
        var closing = false;
        var view = view_array[i];
        JSXArray.push(convert_to_xml_tags(view.type, view.id, closing));
        add_stylesheet_entry(Stylesheet, view);
        recurse_build_jsx_and_stylesheet (JSXArray, Stylesheet, view.children);
        closing = true;
        JSXArray.push(convert_to_xml_tags(view.type, view.id, closing));
    }
}

function build_jsx_and_stylesheet (view_json, callback) {
    var JSXArray = [];
    var Stylesheet = [];
    JSXArray.push("<View style={_root}>");
    recurse_build_jsx_and_stylesheet(JSXArray, Stylesheet, view_json["root"]["children"]);
    JSXArray.push("</View>");
    callback(JSXArray, Stylesheet);
}


function generate_react() {
    var filePath = './js/test/index.android.js';
    var writable = fs.createWriteStream(filePath);
    var readable = fs.createReadStream('react_template/android_template_1.js');
    readable.pipe(writable);
    writable.on('finish', function () {
        var writable = fs.createWriteStream(filePath, { flags: 'a' });
        var readable = fs.createReadStream('react_template/android_template_2.js');
        get_json(function (success, view_json) {
            build_jsx_and_stylesheet(view_json, function (JSXArray, Stylesheet) {
                for (var i in JSXArray) {
                    writable.write(JSXArray[i]);
                    writable.write("\n");
                }
                readable.pipe(writable);
                writable.on('finish', function () {
                    var writable = fs.createWriteStream(filePath, { flags: 'a' });
                    for (var i in Stylesheet) {
                        writable.write(Stylesheet[i]);
                        writable.write("\n");
                    }
                    var readable = fs.createReadStream('react_template/android_template_3.js');
                    readable.pipe(writable);
                }); 
            });
        });
    });
}

generate_react();
