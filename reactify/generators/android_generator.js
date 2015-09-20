function container (id, closing) {
    if (!closing) {
        return "<View style={styles." + id + "}>";
    } else {
        return "</View>";
    }
}

function text_view (id, closing) {
    if (!closing) {
        return "<Text style={styles." + id + "}>\nLorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.";
    } else {
        return "</Text>";
    }
}

function image_view (id, closing) {
    if (!closing) {
        return "<Image source={{uri: 'http://static5.businessinsider.com/image/511d104a69bedd1f7c000012/grumpy-cat-definitely-did-not-make-100-million.jpg'}} style={styles." + id + "}/>";
    } else {
        return "";
    }
}

function button_view (id, closing) {
    if (!closing) {
        return "<TouchableHighlight style={styles." + id + "}>\n<Text style={styles.text_view}>Button</Text>";
    } else {
        return "</TouchableHighlight>";
    }
}

module.exports = {
    get_xml_tag : function (type, id, closing) {
        switch (type) {
            case 'container':
                return container(id, closing);
            case 'text_view':
                return text_view(id, closing);
            case 'image_view':
                return image_view(id, closing);
            case 'button_view':
                return button_view(id, closing);
            default:
                return false;
        }
    }
};
