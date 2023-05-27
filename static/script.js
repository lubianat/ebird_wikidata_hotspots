$(function() {
  $("#city").autocomplete({
      serviceUrl: "https://nominatim.openstreetmap.org/search?format=json",
      paramName: "q",
      transformResult: function(response) {
          var data = JSON.parse(response);
          return {
              suggestions: $.map(data, function(item) {
                  return { value: item.display_name, data: { lat: item.lat, lon: item.lon } };
              })
          };
      },
      onSelect: function (suggestion) {
          $("#lat").val(suggestion.data.lat);
          $("#lng").val(suggestion.data.lon);
      }
  });
});
