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

module.exports = {
    get_xml_tag : function (type, id, closing) {
        switch (type) {
            case 'container' :
                return container(id, closing);
            case 'text_view' :
                return text_view(id, closing);
            default:
                return false;
        }
    }
};
