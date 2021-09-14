angular.module("CAMEL").directive("timeChart", function ($location, Field) {
  return {
    restrict: "E",
    templateUrl: "app/shared/timeChart/timeChart.html",
    scope: {
      fieldTitle: "@",
      chartHeight: "@?",
    },
    link: function (scope, elem, attr) {
      //set default chart height
      if (!this.hasOwnProperty("chartHeight")) {
        scope.chartHeight = "500px";
      }

      var wgsStats = Field.get(
        { id: scope.fieldTitle, timeline: 1 },
        function () {
          var wgsChart = echarts.init(
            document.getElementById("chart-" + scope.fieldTitle)
          );

          timeline = wgsStats.values;

          years = timeline.map((x) => x.year);
          //a continuous 'years' axis
          min_year = Math.min.apply(Math, years);
          max_year = Math.max.apply(Math, years);
          year_span = max_year - min_year + 1;
          cont_years = Array.apply(undefined, Array(year_span)).map(function (
            val,
            index
          ) {
            return index + min_year;
          });

          //gather data per technology
          stats = {};
          for (var i = 0; i < timeline.length; i++) {
            timepoint = timeline[i];
            if (!stats.hasOwnProperty(timepoint.value)) {
              stats[timepoint.value] = {};
            }
            stats[timepoint.value][timepoint.year] = parseInt(timepoint.number);
          }

          //straighten out data (one value per year)
          //and format for eCharts
          datalines = [];
          for (cat in stats) {
            if (stats.hasOwnProperty(cat)) {
              max = 0;
              full_year_list = cont_years.map(function (val, index) {
                if (stats[cat].hasOwnProperty(val)) {
                  max += stats[cat][val];
                }
                return max;
              });

              line = {
                name: cat,
                type: "line",
                smooth: true,
                data: full_year_list,
              };
              datalines.push(line);
            }
          }

          wgsChart.setOption({
            tooltip: {
              trigger: "axis",
            },
            // legend:{},
            xAxis: {
              type: "category",
              boundaryGap: false,
              data: cont_years,
            },
            yAxis: {
              name: "# experiments",
            },
            series: datalines,
          });
        }
      );
    },
  };
});
