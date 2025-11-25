import { createCampusMap } from '../lib/main';

import './style.css';

const map = createCampusMap(document.querySelector('#app') as HTMLElement);

map.on('click', (e) => {
  console.log(e.lngLat.wrap());
});
