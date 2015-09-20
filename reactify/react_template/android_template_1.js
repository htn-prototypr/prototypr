'use strict';

var React = require('react-native');

var {
    AppRegistry,
    StyleSheet,
    Text,
    View,
    Image,
    TouchableHighlight,
    DrawerLayoutAndroid
} = React;

var Test = React.createClass({
    render: function () {
        return (
            <DrawerLayoutAndroid
                renderNavigationView={() => <Text>Test App</Text>}>
