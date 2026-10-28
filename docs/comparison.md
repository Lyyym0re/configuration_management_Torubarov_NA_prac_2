# Сравнение с NuGet, 28 октября 2026 года

Реально выполнены dotnet restore, dotnet package list --include-transitive
и dotnet nuget why для каждого пакета в трёх проектах net10.0.
SDK: 10.0.403. Корневые версии точно зафиксированы как [9.0.0].

| Пакет версии 9.0.0 | Наш граф | NuGet net10.0 |
| --- | ---: | ---: |
| Microsoft.Extensions.DependencyInjection | 10 | 2 |
| Microsoft.Extensions.Options | 89 | 3 |
| Microsoft.Extensions.Logging | 93 | 6 |

Корень включён в подсчёт. Все точные пары имя/версия штатного результата
присутствуют в нашем графе; дополнительных узлов только у NuGet нет.
Наш инструмент объединяет группы всех платформ, включая старые .NET Framework
и .NET Standard. Штатный NuGet выбирает совместимую группу для одного net10.0
и разрешает конфликты в рамках проекта. Поэтому в нашем графе больше узлов.
Например, System.Numerics.Vectors 4.5.0 ведёт к NETStandard.Library 1.6.1
и большой группе старых System.* и runtime.*. В проекте net10.0 этой ветви нет.

Штатное дерево Options: Options → DependencyInjection.Abstractions, Primitives.
В Logging к ним добавляются DependencyInjection и Logging.Abstractions.
У DependencyInjection остаются корень и DependencyInjection.Abstractions.
Все эти пакеты имеют версию 9.0.0 и входят в наши соответствующие графы.

PNG и исходные результаты находятся локально в output/comparison/.
Для повторения сравнения: tools/compare.ps1 (.NET 10 SDK).
Приложение не использует dotnet для получения зависимостей — он нужен только
для отдельного сравнения. PNG, SDK, JAR и пакеты исключены из Git.

Документация штатных средств:
- https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-package-list
- https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-nuget-why
