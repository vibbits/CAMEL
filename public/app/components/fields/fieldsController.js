angular
  .module("CAMEL")
  .controller(
    "FieldsController",
    function ($scope, $location, $sce, Field, State) {
      var ctrl = this;
      ctrl.loaded = false;
      ctrl.reordered = false;

      ctrl.fields = Field.query(function () {
        ctrl.loaded = true;

        for (var field_i in ctrl.fields) {
          if (ctrl.fields.hasOwnProperty(field_i)) {
            var field = ctrl.fields[field_i];
            if (field.options) {
              field.show_options = true;
            } else {
              field.show_options = false;
            }
          }
        }

        var indexDragging = 0;
        $("#fieldstable").sortable({
          update: function (event, ui) {
            newIndex = ui.item.index();
            spliceItem = ctrl.fields.splice(indexDragging, 1)[0];
            ctrl.fields.splice(newIndex, 0, spliceItem);
            spliceItem.changed = true;
            $scope.$apply();
          },
          start: function (event, ui) {
            indexDragging = ui.item.index();
            ctrl.reordered = true;
          },
        });
        $("#fieldstable").disableSelection();
      });

      ctrl.newRow = function () {
        var newField = {
          title: "",
          unit: "",
          description: "",
          options: "",
          type_column: "value_VARCHAR",
          link: 0,
          required: 0,
          weight: 9000,
          group: 0,
          group_id: null,
          new_field: true,
        };
        ctrl.fields.push(newField);
      };

      function deleteRow(field) {
        if (!field.new_field) {
          field.$delete();
        }

        var toDelete = [field];
        //remove dependent fields
        if (field.group) {
          var gid = field.id;
          for (var f in ctrl.fields) {
            var subField = ctrl.fields[f];
            if (subField.hasOwnProperty("group_id")) {
              if (subField.group_id == gid) {
                toDelete.push(subField);
              }
            }
          }
        }

        for (var f in toDelete) {
          var delField = toDelete[f];
          var index = ctrl.fields.indexOf(delField);
          if (index !== -1) {
            ctrl.fields.splice(index, 1);
          }
        }

        State.refresh();
      }

      var confirmAction;
      $scope.warningTitle = "Warning";
      $scope.warningMessage = "Careful there";

      ctrl.type_changed = function (field) {
        if (field.type_column != "value_VARCHAR") {
          field.show_options = false;
        }
        field.changed = true;
      };

      ctrl.confirm = function (confirmData) {
        confirmAction(confirmData);
        $("#confirmModal").modal("hide");
      };

      ctrl.removeRow = function (field) {
        if (!field.new_field) {
          $scope.warningTitle = "Delete field";
          var warningMessage =
            "Deleting a field cannot be undone. <br>" +
            " If this field contains data for any experiments, this data will be lost.";
          if (field.group) {
            warningMessage +=
              "<br><br>" +
              "This field is labeled as a group field, which means all " +
              "dependent fields will also be deleted together with their data.";
          }
          if (field.type_column == "value_ATTACH") {
            warningMessage +=
              "<br><br>" +
              "All attachments of this field type will be deleted.";
          }
          $scope.warningMessage = $sce.trustAsHtml(warningMessage);
          $scope.confirmData = field;
          confirmAction = deleteRow;
          $("#confirmModal").modal();
        } else {
          deleteRow(field);
        }
      };

      ctrl.saveChanges = function () {
        $scope.fieldUpdateForm.$submitted = true;
        if ($scope.fieldUpdateForm.$invalid) {
          return;
        }

        for (var f in ctrl.fields) {
          if (ctrl.fields.hasOwnProperty(f)) {
            var field = ctrl.fields[f];
            if (!field.show_options) {
              field.options = "";
            }
            if (field.new_field) {
              newField = new Field(field);
              newField.weight = Number(f) + 1;
              ctrl.fields[f] = newField;
              newField.$save();
            } else if (
              field.hasOwnProperty("weight") &&
              (field.changed || ctrl.reordered)
            ) {
              field.weight = Number(f) + 1;
              field.$update();
              field.changed = false;
            }
          }
        }
        //Force the ExperimentsController to reload the fields
        State.refresh();
        ctrl.reordered = false;
        $scope.fieldUpdateForm.$submitted = false;
        $scope.fieldUpdateForm.$pristine = true;
      };

      ctrl.cancel = function () {
        $location.path("home");
      };
    }
  );
