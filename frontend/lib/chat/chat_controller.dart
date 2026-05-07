import 'dart:async';

import 'package:flutter/foundation.dart';

import 'chat_chunk.dart';
import 'chat_client.dart';
import 'chat_message.dart';

/// Drives the chat panel: holds the transcript, accumulates streaming deltas,
/// and persists `thread_id` across turns so multi-turn refinement (5/7) works
/// without further plumbing.
class ChatController extends ChangeNotifier {
  ChatController({ChatClient? client}) : _client = client ?? ChatClient();

  final ChatClient _client;
  final List<ChatMessage> _messages = [];
  String? _threadId;
  StreamSubscription<ChatChunk>? _activeStream;
  ChatMessage? _activeAssistant;
  int _seq = 0;

  List<ChatMessage> get messages => List.unmodifiable(_messages);
  bool get isStreaming => _activeStream != null;

  Future<void> send(String text) async {
    final trimmed = text.trim();
    if (trimmed.isEmpty || isStreaming) return;

    _messages.add(ChatMessage(
      id: _nextId('u'),
      role: ChatRole.user,
      text: trimmed,
    ));
    final assistant = ChatMessage(
      id: _nextId('a'),
      role: ChatRole.assistant,
      isStreaming: true,
    );
    _messages.add(assistant);
    _activeAssistant = assistant;
    notifyListeners();

    try {
      final stream = _client.stream(message: trimmed, threadId: _threadId);
      _activeStream = stream.listen(
        _handleChunk,
        onError: (Object err) => _completeWithError(err.toString()),
        onDone: _finalizeStream,
        cancelOnError: true,
      );
    } catch (err) {
      _completeWithError(err.toString());
    }
  }

  void _handleChunk(ChatChunk chunk) {
    final assistant = _activeAssistant;
    if (assistant == null) return;

    switch (chunk.type) {
      case ChatChunkType.text:
        final delta = chunk.payload['delta'] as String? ?? '';
        if (delta.isNotEmpty) {
          assistant.text += delta;
          notifyListeners();
        }
      case ChatChunkType.toolCall:
        final name = chunk.payload['name'] as String? ?? '';
        assistant.toolCallNote = _toolLabel(name);
        notifyListeners();
      case ChatChunkType.proposal:
        assistant.proposal = ScheduleProposal.fromJson(chunk.payload);
        notifyListeners();
      case ChatChunkType.done:
        final tid = chunk.payload['thread_id'] as String?;
        if (tid != null && tid.isNotEmpty) {
          _threadId = tid;
        }
      case ChatChunkType.error:
        assistant.errorMessage =
            chunk.payload['message'] as String? ?? '알 수 없는 오류';
        notifyListeners();
      case ChatChunkType.unknown:
        break;
    }
  }

  void _finalizeStream() {
    _activeAssistant?.isStreaming = false;
    _activeAssistant = null;
    _activeStream = null;
    notifyListeners();
  }

  void _completeWithError(String message) {
    final assistant = _activeAssistant;
    if (assistant != null) {
      assistant.errorMessage = message;
      assistant.isStreaming = false;
    }
    _activeAssistant = null;
    _activeStream?.cancel();
    _activeStream = null;
    notifyListeners();
  }

  String _nextId(String prefix) {
    _seq += 1;
    return '$prefix$_seq';
  }

  static String _toolLabel(String toolName) {
    return switch (toolName) {
      'get_calendar' => '캘린더 확인 중…',
      'get_health' => '컨디션 확인 중…',
      'get_workouts' => '최근 운동 확인 중…',
      '' => '',
      _ => '$toolName 실행 중…',
    };
  }

  @override
  void dispose() {
    _activeStream?.cancel();
    _client.dispose();
    super.dispose();
  }
}
