import {
  AttributionControl,
  GeolocateControl,
  LngLatBounds,
  Map as MapLibre,
  NavigationControl,
  ScaleControl,
} from 'maplibre-gl';
import buildingsSrc from './buildings.geojson?url';
import streetsSrc from './streets.geojson?url';
import terrainsSrc from './terrains.geojson?url';

import './maplibre-gl.css';

export function createCampusMap(container: HTMLElement): MapLibre {
  const bounds = new LngLatBounds(
    [137.401885986328, 34.6975902563304],
    [137.415618896484, 34.7043644344585],
  );
  const maxBounds = new LngLatBounds(
    [
      bounds.getWest() - (bounds.getEast() - bounds.getWest()) / 2,
      bounds.getSouth() - (bounds.getNorth() - bounds.getSouth()) / 2,
    ],
    [
      bounds.getEast() + (bounds.getEast() - bounds.getWest()) / 2,
      bounds.getNorth() + (bounds.getNorth() - bounds.getSouth()) / 2,
    ],
  );

  const map = new MapLibre({
    container,
    style: {
      version: 8,
      sources: {
        terrains: {
          type: 'geojson',
          data: terrainsSrc,
        },
        streets: {
          type: 'geojson',
          data: streetsSrc,
        },
        buildings: {
          type: 'geojson',
          data: buildingsSrc,
        },
      },
      layers: [
        {
          id: 'background',
          type: 'background',
          paint: {
            'background-color': '#F6F8FA',
          },
        },
        {
          id: 'terrains-fill',
          type: 'fill',
          source: 'terrains',
          paint: {
            'fill-color': '#CCF0D7',
          },
        },
        {
          id: 'streets-fill',
          type: 'fill',
          source: 'streets',
          paint: {
            'fill-color': '#E6E6E6',
          },
        },
        {
          id: 'streets-line',
          type: 'line',
          source: 'streets',
          paint: {
            'line-color': '#8B8B8B',
          },
        },
        {
          id: 'buildings-fill',
          type: 'fill',
          source: 'buildings',
          paint: {
            'fill-color': '#DFD0D8',
          },
        },
      ],
      // glyphs: 'https://glyphs.geolonia.com/{fontstack}/{range}.pbf',
    },
    bounds,
    maxBounds,
    attributionControl: false,
    localIdeographFontFamily: 'sans-serif'
  });

  map.addControl(new ScaleControl(), 'bottom-left');

  map.addControl(
    new AttributionControl({
      compact: true,
      customAttribution: '国土地理院ベクトルタイルを加工して作成',
    }),
    'bottom-right',
  );

  map.addControl(
    new GeolocateControl({
      positionOptions: {
        enableHighAccuracy: true,
      },
      trackUserLocation: true,
      fitBoundsOptions: {
        maxZoom: 18,
      },
    }),
    'bottom-right',
  );

  map.addControl(new NavigationControl(), 'bottom-right');

  return map;
}
