export type Direction = 'NORTH' | 'SOUTH' | 'EAST' | 'WEST';

export type TrafficSignal = 'RED' | 'YELLOW' | 'GREEN';

export type SignalPhase = 
  | 'NORTH_SOUTH_GREEN' 
  | 'NORTH_SOUTH_YELLOW' 
  | 'ALL_RED_TRANSITION_1'
  | 'EAST_WEST_GREEN' 
  | 'EAST_WEST_YELLOW'
  | 'ALL_RED_TRANSITION_2';

export type ControllerMode = 'ADAPTIVE' | 'FIXED';

export type CongestionLevel = 'CLEAR' | 'MODERATE' | 'OVERCROWDED';

export interface Coordinates {
  lat: number;
  lng: number;
}

export interface JunctionNode extends Coordinates {
  id: string;
  name: string;
  address: string;
  geofenceRadiusMeters: number;
}

export interface UserSignalAdvice {
  title: string;
  message: string;
  severity: 'info' | 'warning' | 'alert';
  action: 'PROCEED' | 'HOLD' | 'PREPARE_GREEN' | 'REROUTE';
  etaSeconds: number;
  alternateRouteBenefit?: string;
}

export interface TrackedUser extends Coordinates {
  id: string;
  name: string;
  distanceMeters: number;
  distanceToJunctionMeters?: number;
  corridor: Direction;
  speedKmh: number;
  isCurrentDeviceUser?: boolean;
  advice: UserSignalAdvice;
  lastPingTime: number;
}

export interface CorridorStatus {
  direction: Direction;
  name: string;
  activeUsersCount: number;
  usersInInnerZone: number; // < 150m
  usersInOuterZone: number; // 150m - 500m
  avgSpeedKmh: number;
  congestionLevel: CongestionLevel;
  saturationPercentage: number;
  optimalClearingTimeSeconds: number;
  rerouteAdvised: boolean;
}

export interface Vehicle {
  id: string;
  direction: Direction;
  enteredAt: number;
  isEmergency?: boolean;
}

export interface LaneData {
  direction: Direction;
  name: string;
  arrivalRatePerMin: number;
  queue: Vehicle[];
  totalServed: number;
  totalWaitTime: number;
  hasEmergency: boolean;
}

export interface SimulationStats {
  totalServed: number;
  totalWaitTime: number;
  avgWaitTime: number;
  maxWaitTime: number;
  fixedBaselineAvgWait: number;
  delayReductionPercent: number;
  fuelSavedLiters: number;
  co2SavedKg: number;
}

export interface PresetScenario {
  id: string;
  name: string;
  description: string;
  rates: Record<Direction, number>;
}
