angular.module("CAMEL").directive("filesModel", function () {
  return {
    controller: function ($parse, $element, $attrs, $scope) {
      var exp = $parse($attrs.filesModel);

      $element.on("change", function () {
        exp.assign($scope, this.files);
        $scope.$apply();
      });
    },
  };
});
