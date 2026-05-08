import 'package:flutter/foundation.dart';

import 'chat_message.dart';

/// Broadcasts the latest [ScheduleProposal] received from the agent to any
/// listener outside the chat panel (radar card, calendar card, ...).
///
/// Kept separate from `ChatController` so the controller stays focused on the
/// transcript and multiple widgets can listen without coupling to chat state.
class ProposalNotifier extends ChangeNotifier {
  ScheduleProposal? _latest;

  ScheduleProposal? get latest => _latest;

  void update(ScheduleProposal proposal) {
    _latest = proposal;
    notifyListeners();
  }
}
