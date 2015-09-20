'use strict';

var React = require('react-native');
var {
    AppRegistry,
    StyleSheet,
    Text,
    View,
} = React;

var SampleApp = React.createClass({
    render: function () {
        return (
<View style={_root}>
<View style={temp_one}>
</View>
<View style={temp_two}>
</View>
</View>
        );
    }
});

var styles = StyleSheet.create({
temp_one: {
    marginTop: 10,
    marginLeft: 10,
    width: 10,
    height: 10,
},
temp_two: {
    marginTop: 30,
    marginLeft: 10,
    width: 10,
    height: 10,
},
});

AppRegistry.registerComponent('SampleApp', () => SampleApp);
