---
Domain: Modules.Md
Capability: Modules
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

graph LR
  subgraph app
    app_di[app.di]
    app_router[app.router]
  end

  subgraph contracts
    contracts_account[contracts.account]
    contracts_app_version[contracts.app_version]
    contracts_auth[contracts.auth]
    contracts_chores[contracts.chores]
    contracts_expenses[contracts.expenses]
    contracts_flow[contracts.flow]
    contracts_homes[contracts.homes]
    contracts_media[contracts.media]
    contracts_mood[contracts.mood]
    contracts_onboarding[contracts.onboarding]
    contracts_paywall[contracts.paywall]
    contracts_preferences[contracts.preferences]
    contracts_profile[contracts.profile]
    contracts_profile_settings[contracts.profile_settings]
    contracts_share[contracts.share]
    contracts_time[contracts.time]
  end

  subgraph core
    core_account[core.account]
    core_app_version[core.app_version]
    core_auth[core.auth]
    core_config[core.config]
    core_di[core.di]
    core_logging[core.logging]
    core_media[core.media]
    core_network[core.network]
    core_notifications[core.notifications]
    core_onboarding[core.onboarding]
    core_platform[core.platform]
    core_profile[core.profile]
    core_purchases[core.purchases]
    core_share[core.share]
    core_supabase[core.supabase]
    core_theme[core.theme]
    core_time[core.time]
    core_ui[core.ui]
    core_utils[core.utils]
  end

  subgraph features
    features_auth[features.auth]
    features_flow[features.flow]
    features_harmony[features.harmony]
    features_home[features.home]
    features_home_membership[features.home_membership]
    features_nps[features.nps]
    features_offline[features.offline]
    features_paywall[features.paywall]
    features_preferences[features.preferences]
    features_profile_settings[features.profile_settings]
    features_share[features.share]
    features_splash[features.splash]
    features_version_gating[features.version_gating]
    features_welcome[features.welcome]
  end

  subgraph foundation
    foundation_registry[foundation.registry]
    foundation_surfaces[foundation.surfaces]
  end

  subgraph generated
    generated[generated]
  end

  subgraph main
    main_dart[main.dart]
  end

  %% FIX: subgraph id "renderer" conflicted with node id "renderer"
  %% We keep the subgraph name, but rename the node id to renderer_module
  subgraph renderer
    renderer_module[renderer]
  end

  app_di --> core_di
  app_router --> features_splash
  app_router --> foundation_surfaces
  app_router --> features_nps
  app_router --> features_welcome
  app_router --> features_flow
  app_router --> core_auth
  app_router --> features_home_membership
  app_router --> features_version_gating
  app_router --> features_paywall
  app_router --> features_harmony
  app_router --> features_profile_settings
  app_router --> features_preferences
  app_router --> features_share

  contracts_chores --> contracts_time
  contracts_expenses --> contracts_time
  contracts_flow --> contracts_chores
  contracts_homes --> contracts_time
  contracts_mood --> contracts_time
  contracts_share --> contracts_expenses

  core_account --> contracts_account
  core_auth --> contracts_homes
  core_auth --> contracts_profile
  core_media --> contracts_media
  core_notifications --> contracts_profile
  core_onboarding --> contracts_onboarding

  features_flow --> contracts_chores
  features_flow --> core_utils
  features_flow --> contracts_flow
  features_flow --> core_supabase
  features_flow --> app_router
  features_flow --> core_ui
  features_flow --> core_di
  features_flow --> contracts_homes
  features_flow --> contracts_paywall

  features_harmony --> core_supabase
  features_harmony --> app_router
  features_harmony --> core_di
  features_harmony --> contracts_homes
  features_harmony --> core_time
  features_harmony --> contracts_mood

  features_home --> contracts_homes
  features_home --> core_supabase

  features_home_membership --> contracts_homes
  features_home_membership --> app_router

  features_nps --> app_router
  features_nps --> core_di
  features_nps --> contracts_mood

  features_paywall --> app_router
  features_paywall --> core_ui
  features_paywall --> core_di
  features_paywall --> core_logging
  features_paywall --> contracts_homes
  features_paywall --> core_purchases
  features_paywall --> contracts_auth
  features_paywall --> contracts_paywall
  features_paywall --> core_theme

  features_preferences --> app_router
  features_preferences --> core_di
  features_preferences --> core_ui
  features_preferences --> contracts_preferences
  features_preferences --> generated
  features_preferences --> core_theme

  features_profile_settings --> core_supabase
  features_profile_settings --> contracts_profile
  features_profile_settings --> app_router
  features_profile_settings --> core_di
  features_profile_settings --> core_profile
  features_profile_settings --> contracts_profile_settings

  features_share --> core_supabase
  features_share --> app_router
  features_share --> core_ui
  features_share --> core_di
  features_share --> contracts_share
  features_share --> contracts_homes
  features_share --> contracts_paywall
  features_share --> contracts_expenses

  features_splash --> app_router
  features_version_gating --> app_router
  features_welcome --> app_router

  foundation_surfaces --> contracts_flow
  foundation_surfaces --> contracts_profile
  foundation_surfaces --> core_ui
  foundation_surfaces --> contracts_homes
  foundation_surfaces --> app_router
  foundation_surfaces --> core_logging
  foundation_surfaces --> contracts_share
  foundation_surfaces --> core_notifications
  foundation_surfaces --> contracts_expenses
  foundation_surfaces --> core_theme
  foundation_surfaces --> core_di
  foundation_surfaces --> contracts_preferences
  foundation_surfaces --> contracts_profile_settings
  foundation_surfaces --> core_platform
  foundation_surfaces --> contracts_chores
  foundation_surfaces --> contracts_account
  foundation_surfaces --> generated
  foundation_surfaces --> core_config
  foundation_surfaces --> contracts_paywall
  foundation_surfaces --> contracts_onboarding
  foundation_surfaces --> contracts_mood

  %% FIX: edges should reference the node id, not the subgraph id
  renderer_module --> contracts_homes
  renderer_module --> contracts_paywall
  renderer_module --> contracts_share