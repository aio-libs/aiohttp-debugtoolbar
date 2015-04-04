
require.config({
  paths: {
    "jquery": "jquery-1.7.2.min",
  }
});

require(["jquery"], function($) {
  $(function() {
    console.log('TEST REQUIREJS');
  });
});

define("main", function(){});
