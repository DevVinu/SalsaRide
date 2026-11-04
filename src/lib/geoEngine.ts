import {
  Coordinates,
  Direction,
  JunctionNode,
  TrackedUser,
  CorridorStatus,
  UserSignalAdvice,
  SignalPhase,
} from '../types/traffic';

/**
 * Calculates great-circle distance between two coordinates in meters (Haversine formula)
 */
export function calculateHaversineDistanceMeters(
  point1: Coordinates,
  point2: Coordinates
): number {
  const R = 6371e3; // Earth radius in meters
  const phi1 = (point1.lat * Math.PI) / 180;
  const phi2 = (point2.lat * Math.PI) / 180;
  const deltaPhi = ((point2.lat - point1.lat) * Math.PI) / 180;
  const deltaLambda = ((point2.lng - point1.lng) * Math.PI) / 180;

  const a =
    Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
    Math.cos(phi1) * Math.cos(phi2) * Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return Math.round(R * c);
}

/**
 * Calculates initial compass bearing from point1 to point2 in degrees (0 - 360)
 */
export function calculateBearing(point1: Coordinates, point2: Coordinates): number {
  const lat1 = (point1.lat * Math.PI) / 180;
  const lat2 = (point2.lat * Math.PI) / 180;
  const diffLng = ((point2.lng - point1.lng) * Math.PI) / 180;

  const y = Math.sin(diffLng) * Math.cos(lat2);
  const x =
    Math.cos(lat1) * Math.sin(lat2) -
    Math.sin(lat1) * Math.cos(lat2) * Math.cos(diffLng);

  let brng = (Math.atan2(y, x) * 180) / Math.PI;
  return (brng + 360) % 360;
}

/**
 * Maps a location relative to the junction to a corridor approach direction
 */
export function getCorridorDirection(userLoc: Coordinates, junctionLoc: Coordinates): Direction {
  // Bearing from junction to user
  const bearing = calculateBearing(junctionLoc, userLoc);

  if (bearing >= 315 || bearing < 45) {
    return 'NORTH';
  } else if (bearing >= 45 && bearing < 135) {
    return 'EAST';
  } else if (bearing >= 135 && bearing < 225) {
    return 'SOUTH';
  } else {
    return 'WEST';
  }
}

/**
 * Predefined sample city intersections
 */
export const SAMPLE_JUNCTIONS: JunctionNode[] = [
  {
    id: 'metro_junction_1',
    name: 'Grand Central & 42nd Crossing',
    address: 'Park Ave & E 42nd St, New York, NY',
    lat: 40.7516,
    lng: -73.9767,
    geofenceRadiusMeters: 500,
  },
  {
    id: 'metro_junction_2',
    name: 'Tech Corridor Central Ring',
    address: 'Market St & 4th St, San Francisco, CA',
    lat: 37.7857,
    lng: -122.4064,
    geofenceRadiusMeters: 500,
  },
  {
    id: 'metro_junction_3',
    name: 'Downtown Commercial Hub',
    address: 'Galle Road & Colpetty Junction, Colombo',
    lat: 6.9015,
    lng: 79.8517,
    geofenceRadiusMeters: 500,
  },
];

/**
 * Generates initial realistic simulated active users around the junction
 */
export function generateInitialUsers(junction: JunctionNode): TrackedUser[] {
  const users: TrackedUser[] = [];
  const corridorOffsets: Record<Direction, { latFactor: number; lngFactor: number }> = {
    NORTH: { latFactor: 1, lngFactor: 0 },
    SOUTH: { latFactor: -1, lngFactor: 0 },
    EAST: { latFactor: 0, lngFactor: 1 },
    WEST: { latFactor: 0, lngFactor: -1 },
  };

  // Heavy traffic on North corridor (simulate overcrowding scenario)
  const corridorCounts: Record<Direction, number> = {
    NORTH: 14,
    SOUTH: 8,
    EAST: 4,
    WEST: 3,
  };

  let counter = 1;
  (Object.keys(corridorCounts) as Direction[]).forEach((dir) => {
    const count = corridorCounts[dir];
    const offset = corridorOffsets[dir];

    for (let i = 0; i < count; i++) {
      // Distance between 40m and 480m along corridor line with slight jitter
      const distanceFraction = 0.08 + (i / count) * 0.85;
      const meterDist = Math.round(distanceFraction * junction.geofenceRadiusMeters);
      
      // Rough degree approximation: ~111,000 meters per degree
      const deltaLat = (offset.latFactor * meterDist) / 111000 + (Math.random() - 0.5) * 0.0003;
      const deltaLng = (offset.lngFactor * meterDist) / (111000 * Math.cos((junction.lat * Math.PI) / 180)) + (Math.random() - 0.5) * 0.0003;

      const userLoc: Coordinates = {
        lat: junction.lat + deltaLat,
        lng: junction.lng + deltaLng,
      };

      const actualDist = calculateHaversineDistanceMeters(userLoc, junction);
      const isCongestedCorridor = dir === 'NORTH';
      const speed = isCongestedCorridor ? Math.max(3, Math.round(18 - (1 - distanceFraction) * 14)) : Math.round(28 + Math.random() * 15);

      users.push({
        id: `USR-${counter.toString().padStart(3, '0')}`,
        name: `Commuter #${counter}`,
        lat: userLoc.lat,
        lng: userLoc.lng,
        distanceMeters: actualDist,
        corridor: dir,
        speedKmh: speed,
        lastPingTime: Date.now(),
        advice: {
          title: 'Monitoring Route',
          message: 'Tracking real-time corridor flow',
          severity: 'info',
          action: 'PROCEED',
          etaSeconds: Math.round(actualDist / (Math.max(2, speed) * 0.277)),
        },
      });
      counter++;
    }
  });

  return users;
}

/**
 * Analyzes corridors to detect overcrowding and computes shortest jam-solving mechanisms
 */
export function analyzeCorridors(
  junction: JunctionNode,
  users: TrackedUser[],
  activePhase: SignalPhase
): {
  corridors: Record<Direction, CorridorStatus>;
  overcrowdedCorridor: Direction | null;
  recommendedPhase: SignalPhase;
  updatedUsers: TrackedUser[];
} {
  const directions: Direction[] = ['NORTH', 'SOUTH', 'EAST', 'WEST'];

  const corridorBuckets: Record<Direction, TrackedUser[]> = {
    NORTH: [],
    SOUTH: [],
    EAST: [],
    WEST: [],
  };

  // Filter users inside geofence radius and partition
  users.forEach((user) => {
    const dist = calculateHaversineDistanceMeters(user, junction);
    if (dist <= junction.geofenceRadiusMeters) {
      corridorBuckets[user.corridor].push({ ...user, distanceMeters: dist });
    }
  });

  const corridors = {} as Record<Direction, CorridorStatus>;
  let maxCount = -1;
  let overcrowdedDir: Direction | null = null;

  directions.forEach((dir) => {
    const corridorUsers = corridorBuckets[dir];
    const innerZoneUsers = corridorUsers.filter((u) => u.distanceMeters <= 150).length;
    const outerZoneUsers = corridorUsers.filter((u) => u.distanceMeters > 150).length;
    const totalUsers = corridorUsers.length;

    const avgSpeed = totalUsers > 0
      ? Math.round(corridorUsers.reduce((sum, u) => sum + u.speedKmh, 0) / totalUsers)
      : 40;

    let level: 'CLEAR' | 'MODERATE' | 'OVERCROWDED' = 'CLEAR';
    if (totalUsers >= 10 || (totalUsers >= 6 && avgSpeed < 12)) {
      level = 'OVERCROWDED';
    } else if (totalUsers >= 5) {
      level = 'MODERATE';
    }

    const saturationPct = Math.min(100, Math.round((totalUsers / 15) * 100));
    const clearingTime = Math.max(8, Math.min(50, totalUsers * 3));
    const reroute = level === 'OVERCROWDED' && outerZoneUsers >= 5;

    corridors[dir] = {
      direction: dir,
      name: `${dir.charAt(0) + dir.slice(1).toLowerCase()} Approach`,
      activeUsersCount: totalUsers,
      usersInInnerZone: innerZoneUsers,
      usersInOuterZone: outerZoneUsers,
      avgSpeedKmh: avgSpeed,
      congestionLevel: level,
      saturationPercentage: saturationPct,
      optimalClearingTimeSeconds: clearingTime,
      rerouteAdvised: reroute,
    };

    if (totalUsers > maxCount) {
      maxCount = totalUsers;
      if (level === 'OVERCROWDED') {
        overcrowdedDir = dir;
      }
    }
  });

  // Shortest jam-solving signal recommendation
  let recommendedPhase: SignalPhase = 'NORTH_SOUTH_GREEN';
  const nsPressure = corridors.NORTH.activeUsersCount + corridors.SOUTH.activeUsersCount;
  const ewPressure = corridors.EAST.activeUsersCount + corridors.WEST.activeUsersCount;

  if (ewPressure > nsPressure) {
    recommendedPhase = 'EAST_WEST_GREEN';
  } else {
    recommendedPhase = 'NORTH_SOUTH_GREEN';
  }

  // Generate personalized dynamic advice for each active user based on their corridor and distance
  const updatedUsers = users.map((user) => {
    const corridor = corridors[user.corridor];
    const isOvercrowded = corridor.congestionLevel === 'OVERCROWDED';
    const dist = user.distanceMeters;

    let advice: UserSignalAdvice;

    if (isOvercrowded) {
      if (dist <= 140) {
        // At the junction - grant/announce priority green
        advice = {
          title: '⚡ Priority Green Signal Scheduled',
          message: `SalsaRide priority phase active. Green wave allocated (${corridor.optimalClearingTimeSeconds}s). Maintain lane.`,
          severity: 'info',
          action: 'PREPARE_GREEN',
          etaSeconds: 8,
        };
      } else {
        // In the outer bottleneck - advise shortest bypass route
        advice = {
          title: '⚠️ Severe Jam Ahead (Overcrowded Corridor)',
          message: `${corridor.activeUsersCount} users queued ahead. Shortest bypass detour available to skip queue.`,
          severity: 'alert',
          action: 'REROUTE',
          etaSeconds: Math.round(dist / 2.5),
          alternateRouteBenefit: 'Save 7-11 mins via Side Radial Bypass',
        };
      }
    } else if (corridor.congestionLevel === 'MODERATE') {
      advice = {
        title: 'Moderate Inflow',
        message: 'Signals balancing. Estimated stop delay under 20s.',
        severity: 'warning',
        action: 'PROCEED',
        etaSeconds: Math.round(dist / 6),
      };
    } else {
      advice = {
        title: 'Corridor Free Flow',
        message: 'No congestion. Maintain standard speed to pass on green wave.',
        severity: 'info',
        action: 'PROCEED',
        etaSeconds: Math.round(dist / 10),
      };
    }

    return {
      ...user,
      advice,
    };
  });

  return {
    corridors,
    overcrowdedCorridor: overcrowdedDir,
    recommendedPhase,
    updatedUsers,
  };
}

