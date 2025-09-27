// src/lib/leafletIcons.ts
import L from "leaflet";
import { renderToString } from "react-dom/server";
import { MapPin, type LucideProps } from "lucide-react";


function FilledMapPin(props: LucideProps) {
  return <MapPin {...props} fill={props.fill ?? "red"} stroke="none" />;
}

export const hotspotIcon = new L.DivIcon({
  className: "",
  html: renderToString(<FilledMapPin size={24} />),
  iconSize: [24, 24] as [number, number],
  iconAnchor: [12, 24] as [number, number],
  popupAnchor: [0, -24] as [number, number],
});
