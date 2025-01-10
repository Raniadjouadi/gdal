
    localStorage.setItem("tempGeoJson", '{{ppgeojson | safe}}');
    var layerosm = new ol.layer.Tile({source: new ol.source.OSM()})
    var style = function(feature, resolution){
      var context = {
          feature: feature,
          variables: {}
      };
      var value = ""
      var labelText = "";
      size = 0;
      var labelFont = "10px, sans-serif";
      var labelFill = "#000000";
      var bufferColor = "";
      var bufferWidth = 0;
      var textAlign = "left";
      var offsetX = 8;
      var offsetY = 3;
      var placement = 'point';
      if ("" !== null) {
          labelText = String("");
      }
      var style = [ new ol.style.Style({
          image: new ol.style.Circle({radius: 3.0 + size,
                                      stroke: new ol.style.Stroke({color: 'rgba(35,35,35,0.5)', 
                                                                    lineDash: null, 
                                                                    lineCap: 'butt', 
                                                                    lineJoin: 'miter', 
                                                                    width: 0
                                                                  }), 
                                      fill: new ol.style.Fill({color: 'rgba(255,0,0,1.0)'})
                                    })
          })];
          return style;}


//      var source = new ol.source.Vector({url: 'data:,' + encodeURIComponent('{{ppgeojson | safe}}'),format: new ol.format.GeoJSON()})
    var source = new ol.source.Vector()
    
    var layervecteur = new ol.layer.Vector({source:source, style:style})
    
    var map = new ol.Map({
      target: 'map',
      layers: [layerosm,layervecteur],
      view: new ol.View({
        center: ol.proj.fromLonLat([15, 9]),
        zoom: 3.7
      })
    });
      const geojson = JSON.parse('{{ppgeojson | safe}}')
      source.addFeatures(
      new ol.format.GeoJSON().readFeatures(geojson, {
        dataProjection: 'EPSG:4326',
        featureProjection: map.getView().getProjection()
      })
      );
  