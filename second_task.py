import csv
from django.db import models
from django.utils import timezone
from django.db.models import OuterRef, Subquery
from django.http import HttpResponse


class Player(models.Model):
    player_id = models.CharField(max_length=100)


class Level(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)


class Prize(models.Model):
    title = models.CharField(max_length=100)


class PlayerLevel(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)


class LevelPrize(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    received = models.DateField()

    @classmethod
    def assign_prize_to_player(cls, player, level):
        """Присваивает игроку приз за завершение уровня"""
        try:
            player_level = PlayerLevel.objects.get(player=player, level=level)
            
            if player_level.is_completed:
                # Проверяем, есть ли призы для уровня
                level_prize = cls.objects.filter(level=level, received__isnull=True)
                if level_prize.exists():
                    # Присваиваем приз
                    level_prize.received = timezone.now()
                    level_prize.save()
                    return f"Приз '{level_prize.prize.title}' был успешно присвоен игроку '{player.player_id}' за уровень '{level.title}'"
                else:
                    return "Приз для данного уровня не назначен или уже был выдан"
            else:
                return "Игрок не завершил уровень"
        except PlayerLevel.DoesNotExist:
            return "Запись о прохождении уровня не найдена"

    @classmethod
    def export_player_data_to_csv(cls, request):
        """Экспортирует данные игроков и уровней в CSV файл"""
        # Создаем HTTP-ответ с CSV-данными
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="player_data.csv"'

        writer = csv.writer(response)
        # Записываем заголовки
        writer.writerow(['player_id', 'level_title', 'is_completed', 'prize_title'])

        # Выбираем данные для экспорта
        player_levels = PlayerLevel.objects.select_related('player', 'level').annotate(
            prize_title=Subquery(
                cls.objects.filter(level=OuterRef('level'), received__isnull=False).values('prize__title')[:1]
            )
        ).iterator()

        # Записываем строки
        for player_level in player_levels:
            writer.writerow([
                player_level.player.player_id,
                player_level.level.title,
                player_level.is_completed,
                player_level.prize_title or 'Приз не получен'
            ])

        return response