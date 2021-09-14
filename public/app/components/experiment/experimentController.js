angular
  .module("CAMEL")
  .controller(
    "ExperimentController",
    function (
      $scope,
      $location,
      $timeout,
      $routeParams,
      $route,
      $http,
      Experiment,
      Field,
      config
    ) {
      var ctrl = this;

      $scope.download_url = config.attachments;
      $scope.exp = Experiment.get(
        $routeParams,
        function () {
          //experiment loaded
        },
        function () {
          //failed to load
          $location.path("/home");
        }
      );
      $scope.fields = Field.query();

      ctrl.edit = function () {
        $location.path("/experiment/edit/" + $routeParams["id"]);
      };
    }
  );
