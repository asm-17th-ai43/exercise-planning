import 'package:flutter/material.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'api/calendar_api.dart';
import 'api/health_api.dart';
import 'api/workouts_api.dart';
import 'cards/calendar_card.dart';
import 'cards/fatigue_radar_card.dart';
import 'cards/health_card.dart';
import 'cards/workouts_card.dart';
import 'design/app_theme.dart';
import 'design/tokens/colors.dart';
import 'design/tokens/radius.dart';
import 'design/tokens/shadows.dart';
import 'design/tokens/spacing.dart';
import 'design/tokens/typography.dart';
import 'env.dart';
import 'models/muscle_fatigue_state.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await initializeDateFormatting('ko_KR');

  if (Env.isConfigured) {
    await Supabase.initialize(
      url: Env.supabaseUrl,
      anonKey: Env.supabaseAnonKey,
    );
  }

  runApp(const ExercisePlanningApp());
}

class ExercisePlanningApp extends StatelessWidget {
  const ExercisePlanningApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI 운동 코치',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      home: const DashboardPage(),
    );
  }
}

class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    if (!Env.isConfigured) {
      return const _ConfigMissingPage();
    }

    final client = Supabase.instance.client;
    final apis = _DashboardApis(
      calendar: CalendarApi(client),
      health: HealthApi(client),
      workouts: WorkoutsApi(client),
    );
    final weekStart = _mondayOfThisWeek(DateTime.now());

    return Scaffold(
      body: DecoratedBox(
        decoration: const BoxDecoration(gradient: AppColors.pageGradient),
        child: SafeArea(
          child: LayoutBuilder(
            builder: (context, constraints) {
              return SingleChildScrollView(
                padding: const EdgeInsets.symmetric(
                  horizontal: AppSpacing.s7,
                  vertical: AppSpacing.s6,
                ).copyWith(top: AppSpacing.s5),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const _DashboardHeader(),
                    const SizedBox(height: AppSpacing.s6),
                    _DashboardBody(apis: apis, weekStart: weekStart),
                  ],
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}

class _DashboardApis {
  const _DashboardApis({
    required this.calendar,
    required this.health,
    required this.workouts,
  });

  final CalendarApi calendar;
  final HealthApi health;
  final WorkoutsApi workouts;
}

DateTime _mondayOfThisWeek(DateTime now) {
  final date = DateTime(now.year, now.month, now.day);
  return date.subtract(Duration(days: date.weekday - DateTime.monday));
}

class _DashboardHeader extends StatelessWidget {
  const _DashboardHeader();

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Container(
          padding: const EdgeInsets.all(AppSpacing.s3),
          decoration: BoxDecoration(
            color: AppColors.bgElevated1,
            borderRadius: BorderRadius.circular(AppRadius.md),
            border: Border.all(color: AppColors.borderSubtle),
          ),
          child: Icon(
            LucideIcons.bot,
            size: 22,
            color: AppColors.accentPrimary,
          ),
        ),
        const SizedBox(width: AppSpacing.s4),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('AI 운동 코치', style: AppTypography.display),
              const SizedBox(height: 2),
              Text(
                '캘린더, 컨디션, 운동 이력을 종합해 이번 주 맞춤 스케줄을 제안합니다.',
                style: AppTypography.body.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
        ),
        const _GhostButton(icon: LucideIcons.chevronLeft, label: '지난주'),
        const SizedBox(width: AppSpacing.s2),
        const _GhostButton(icon: LucideIcons.chevronRight, label: '다음주'),
      ],
    );
  }
}

class _GhostButton extends StatelessWidget {
  const _GhostButton({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.s3,
        vertical: AppSpacing.s2,
      ),
      decoration: BoxDecoration(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(AppRadius.md),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: AppColors.textSecondary),
          const SizedBox(width: AppSpacing.s1),
          Text(
            label,
            style: AppTypography.caption.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}

class _DashboardBody extends StatelessWidget {
  const _DashboardBody({required this.apis, required this.weekStart});

  final _DashboardApis apis;
  final DateTime weekStart;

  @override
  Widget build(BuildContext context) {
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // 좌측 데이터 영역 (7/12 ≈ 0.58)
          Expanded(
            flex: 7,
            child: _LeftColumn(apis: apis, weekStart: weekStart),
          ),
          const SizedBox(width: AppSpacing.s5),
          // 우측 챗봇 영역 (5/12 ≈ 0.42)
          const Expanded(
            flex: 5,
            child: _ChatPlaceholderPanel(),
          ),
        ],
      ),
    );
  }
}

class _LeftColumn extends StatelessWidget {
  const _LeftColumn({required this.apis, required this.weekStart});

  final _DashboardApis apis;
  final DateTime weekStart;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        CalendarCard(api: apis.calendar, weekStart: weekStart),
        const SizedBox(height: AppSpacing.s5),
        IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Expanded(child: HealthCard(api: apis.health)),
              const SizedBox(width: AppSpacing.s5),
              Expanded(child: WorkoutsCard(api: apis.workouts)),
            ],
          ),
        ),
        const SizedBox(height: AppSpacing.s5),
        FatigueRadarCard(state: MuscleFatigueState.demo()),
      ],
    );
  }
}

class _ChatPlaceholderPanel extends StatelessWidget {
  const _ChatPlaceholderPanel();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.s5),
      decoration: BoxDecoration(
        color: AppColors.bgElevated1,
        borderRadius: BorderRadius.circular(AppRadius.xl),
        border: Border.all(color: AppColors.borderSubtle),
        boxShadow: AppShadows.card,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(AppSpacing.s2),
                decoration: BoxDecoration(
                  color: AppColors.bgElevated2,
                  borderRadius: BorderRadius.circular(AppRadius.full),
                ),
                child: Icon(
                  LucideIcons.bot,
                  size: 18,
                  color: AppColors.accentPrimary,
                ),
              ),
              const SizedBox(width: AppSpacing.s3),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('AI 코치', style: AppTypography.h3),
                    Text(
                      'B 슬라이스 · lib/chat/',
                      style: AppTypography.caption,
                    ),
                  ],
                ),
              ),
              Icon(
                LucideIcons.messageSquarePlus,
                size: 18,
                color: AppColors.textSecondary,
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.s5),
          Expanded(
            child: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    LucideIcons.sparkles,
                    size: 32,
                    color: AppColors.accentPrimaryGlow,
                  ),
                  const SizedBox(height: AppSpacing.s3),
                  Text(
                    '"이번 주 운동 추천해줘"',
                    style: AppTypography.body.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                  const SizedBox(height: AppSpacing.s1),
                  Text(
                    'SSE 스트림 + 추천 슬롯 카드 · 5/8 통합',
                    style: AppTypography.caption.copyWith(
                      color: AppColors.textTertiary,
                    ),
                  ),
                ],
              ),
            ),
          ),
          _ChatInputPlaceholder(),
        ],
      ),
    );
  }
}

class _ChatInputPlaceholder extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      height: 48,
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.s4),
      decoration: BoxDecoration(
        color: AppColors.bgElevated2,
        borderRadius: BorderRadius.circular(AppRadius.full),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Row(
        children: [
          Icon(
            LucideIcons.plusCircle,
            size: 18,
            color: AppColors.textTertiary,
          ),
          const SizedBox(width: AppSpacing.s3),
          Expanded(
            child: Text(
              '메시지를 입력하세요... (B 슬라이스)',
              style: AppTypography.body.copyWith(
                color: AppColors.textTertiary,
              ),
            ),
          ),
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: AppColors.accentSecondary.withValues(alpha: 0.4),
              borderRadius: BorderRadius.circular(AppRadius.md),
            ),
            child: Icon(
              LucideIcons.send,
              size: 16,
              color: AppColors.textPrimary,
            ),
          ),
        ],
      ),
    );
  }
}

class _ConfigMissingPage extends StatelessWidget {
  const _ConfigMissingPage();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: DecoratedBox(
        decoration: const BoxDecoration(gradient: AppColors.pageGradient),
        child: Center(
          child: Container(
            constraints: const BoxConstraints(maxWidth: 520),
            margin: const EdgeInsets.all(AppSpacing.s5),
            padding: const EdgeInsets.all(AppSpacing.s6),
            decoration: BoxDecoration(
              color: AppColors.bgElevated1,
              borderRadius: BorderRadius.circular(AppRadius.xl),
              border: Border.all(color: AppColors.borderSubtle),
              boxShadow: AppShadows.card,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  LucideIcons.keyRound,
                  size: 28,
                  color: AppColors.accentPrimary,
                ),
                const SizedBox(height: AppSpacing.s3),
                Text(
                  'Supabase 키가 설정되지 않았습니다',
                  style: AppTypography.h2,
                ),
                const SizedBox(height: AppSpacing.s2),
                Text(
                  '아래 명령으로 실행하세요. URL/anon key는 팀 채널에서 확인.',
                  style: AppTypography.body.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(height: AppSpacing.s4),
                Container(
                  padding: const EdgeInsets.all(AppSpacing.s4),
                  decoration: BoxDecoration(
                    color: AppColors.bgElevated2,
                    borderRadius: BorderRadius.circular(AppRadius.md),
                    border: Border.all(color: AppColors.borderSubtle),
                  ),
                  child: const SelectableText(
                    'flutter run -d chrome \\\n'
                    '  --dart-define=SUPABASE_URL=https://<project>.supabase.co \\\n'
                    '  --dart-define=SUPABASE_ANON_KEY=<anon-key>',
                    style: TextStyle(
                      fontFamily: 'monospace',
                      color: AppColors.textSecondary,
                      fontSize: 12,
                      height: 1.7,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
