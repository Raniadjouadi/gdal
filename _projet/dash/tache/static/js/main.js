window.onload = init;

function init(){

  const fillStyle = new ol.style.Fill({ color: [250, 188, 50, .2] })
  const strokeStyle = new ol.style.Stroke({ color: [0, 130, 196, 0], width: .5 })
  const circleStyle = new ol.style.Circle({
    fill: new ol.style.Fill({color: [245, 49, 5, 0.5]}),
    radius: 3,
    stroke: new ol.style.Stroke({ color: [0, 0, 45, 1], width: 1 })
  })



  var sourceaoi = new ol.source.Vector()
  
  var layeraoi = new ol.layer.Vector({
    source: sourceaoi,
    title: 'AOIS',
    style: new ol.style.Style({
      fill: fillStyle,
      stroke: strokeStyle,
      image: circleStyle
    }) 
  })


  var sourcepp = new ol.source.Vector()
  
  var layerpp = new ol.layer.Vector({
    source: sourcepp,
    style: new ol.style.Style({
      fill: fillStyle,
      stroke: strokeStyle,
      image: circleStyle
    }) 
  })


  var layerosm = new ol.layer.Tile({source: new ol.source.OSM()})
  const openStreetMapStandard = new ol.layer.Tile({
    source: new ol.source.OSM(),
    visible: false,
    title: 'OSMStandard'
  })




  const map = new ol.Map({
    view: new ol.View({
        center: [ 10, 9 ],
        zoom: 6,
        projection: 'EPSG:4326'
    }),
    layers:[
        new ol.layer.Tile({
            source: new ol.source.OSM()
        })
    ],
    target: 'map'
  })



  sourceaoi.addFeatures(
    new ol.format.GeoJSON().readFeatures({{aoi | safe}}, {
      dataProjection: 'EPSG:4326',
    })
  );


  map.addLayer(layeraoi);

  var extentAoi = sourceaoi.getExtent();
  {% comment %} var extentpp = sourcepp.getExtent(); {% endcomment %}
  {% comment %} console.log(extentAoi); {% endcomment %}
  var extentbuffer = new ol.extent.buffer(extentAoi,2);
  {% comment %} console.log(extentbuffer); {% endcomment %}

  map.getView().fit(extentbuffer, map.getSize());


  // Vector Fe1ature Popup Logic 
  const overlayContainerElement = document.querySelector('.overlay-container');
  const overlayLayer = new ol.Overlay({
    element: overlayContainerElement
  })
  map. addOverlay(overlayLayer);
  const overlayFeatureName = document.getElementById('feature-name');
  //const overlayFeatureAdditionInfo = document.getElementById('feature-additional-info');

  map.on('click', function(e){
    overlayLayer.setPosition(undefined);
    map.forEachFeatureAtPixel(e.pixel, function (feature, layer){
      let clickedCoordinate = e.coordinate;
      let clickedFeatureName = feature.get('name');
      //let clickedFeatureAdditionalInfo = feature.get('additional  info');
      overlayLayer.setPosition(clickedCoordinate); 
      overlayFeatureName.innerHTML = clickedFeatureName; 
      //overlayFeatureAdditionInfo.innerHTML = clickedFeatureAdditionalInfo;
    },
    {
      layerFilter: function(layerCandidate){
        return layerCandidate.get('title') === 'AOIS'
      }
    })
  })

}
