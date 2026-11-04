class VirtualSignalModel {
  final String junctionId;
  final String junctionCode;
  final String currentPhase;
  final int phaseDurationSeconds;
  final int remainingSeconds;
  final int elapsedSeconds;
  final String northSouthLamp;
  final String eastWestLamp;
  final String priorityCorridor;
  final double priorityScoreNs;
  final double priorityScoreEw;
  final String disclaimer;

  VirtualSignalModel({
    required this.junctionId,
    required this.junctionCode,
    required this.currentPhase,
    required this.phaseDurationSeconds,
    required this.remainingSeconds,
    required this.elapsedSeconds,
    required this.northSouthLamp,
    required this.eastWestLamp,
    required this.priorityCorridor,
    required this.priorityScoreNs,
    required this.priorityScoreEw,
    required this.disclaimer,
  });

  factory VirtualSignalModel.fromJson(Map<String, dynamic> json) {
    return VirtualSignalModel(
      junctionId: json['junction_id'] ?? '',
      junctionCode: json['junction_code'] ?? '',
      currentPhase: json['current_phase'] ?? 'NORTH_SOUTH_GREEN',
      phaseDurationSeconds: json['phase_duration_seconds'] ?? 24,
      remainingSeconds: json['remaining_seconds'] ?? 0,
      elapsedSeconds: json['elapsed_seconds'] ?? 0,
      northSouthLamp: json['north_south_lamp'] ?? 'RED',
      eastWestLamp: json['east_west_lamp'] ?? 'RED',
      priorityCorridor: json['priority_corridor'] ?? 'NORTH',
      priorityScoreNs: (json['priority_score_ns'] as num?)?.toDouble() ?? 0.0,
      priorityScoreEw: (json['priority_score_ew'] as num?)?.toDouble() ?? 0.0,
      disclaimer: json['disclaimer'] ?? 'Informational virtual advisory',
    );
  }
}

class UserSignalAdvisoryModel {
  final String junctionId;
  final String corridor;
  final double distanceMeters;
  final String userSignalLamp;
  final int phaseRemainingSeconds;
  final String advisoryTitle;
  final String advisoryMessage;
  final String advisorySeverity;
  final String action;
  final String? detourBenefit;

  UserSignalAdvisoryModel({
    required this.junctionId,
    required this.corridor,
    required this.distanceMeters,
    required this.userSignalLamp,
    required this.phaseRemainingSeconds,
    required this.advisoryTitle,
    required this.advisoryMessage,
    required this.advisorySeverity,
    required this.action,
    this.detourBenefit,
  });

  factory UserSignalAdvisoryModel.fromJson(Map<String, dynamic> json) {
    return UserSignalAdvisoryModel(
      junctionId: json['junction_id'] ?? '',
      corridor: json['corridor'] ?? 'NORTH',
      distanceMeters: (json['distance_meters'] as num?)?.toDouble() ?? 0.0,
      userSignalLamp: json['user_signal_lamp'] ?? 'RED',
      phaseRemainingSeconds: json['phase_remaining_seconds'] ?? 0,
      advisoryTitle: json['advisory_title'] ?? 'Signal Advisory',
      advisoryMessage: json['advisory_message'] ?? '',
      advisorySeverity: json['advisory_severity'] ?? 'info',
      action: json['action'] ?? 'PROCEED',
      detourBenefit: json['detour_benefit'],
    );
  }
}

