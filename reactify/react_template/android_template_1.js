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
                renderNavigationView={() => <Text>HTN Test App</Text>}>
                <View style={styles.actionbar}>
                    <Text style={styles.title}>HTN Test App</Text>
                </View>
