function container (id, closing) {
    if (!closing) {
        return "<View style={" + id + "}>";
    } else {
        return "</View>";
    }
}

module.exports = {
    get_xml_tag : function (type, id, closing) {
        switch (type) {
            case 'container' :
                return container(id, closing);
            default:
                return false;
        }
    }
};
