import argparse
import datetime
import json
import os
import re
import shutil
import sys
from pathlib import Path

# Ensure UTF-8 stdout for Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

# 6 Meta-Review Files to Archive
META_FILES = {
    "can_rigorous_manual_dimensional_consistency_checks_be_performed_by_experts_to_supplement_the_automated_undecidable_result.md",
    "can_the_dimensional_consistency_be_conclusively_verified_using_advanced_symbolic_methods_beyond_current_automated_tools.md",
    "can_you_provide_a_corrected_and_verifiable_bibliography_replacing_the_futuredated_2025_reference_with_established_peerreviewed_material.md",
    "is_it_possible_to_provide_more_detailed_mathematical_derivations_and_dimensional_consistency_checks_to_raise_the_math_verification_score.md",
    "what_specific_mathematical_proofs_or_validations_are_needed_to_resolve_the_current_mathpending_status.md",
    "what_specific_mathematical_subtleties_or_unstated_assumptions_prevented_full_mathematical_integrity_compliance.md",
}

# Curated Concept Renaming Map (61 Files)
CURATED_RENAMES = {
    "are_there_experimental_strategies_to_better_constrain_neutrino_decay_widths_j_and_confirm_decayinclusive_oscillation_modifications.md": (
        "Neutrino Decay Width Constraints and Decay-Inclusive Oscillations",
        "neutrino_decay_width_constraints_and_decay_inclusive_oscillations.md"
    ),
    "are_there_proposed_or_ongoing_calibration_or_control_measurements_designed_to_rule_out_confounding_effects_mimicking_neutrino_decay_signals_in_planned_or_current_detector_setups.md": (
        "Calibration Strategies to Rule Out Confounding Neutrino Decay Signals",
        "calibration_strategies_for_neutrino_decay_signals.md"
    ),
    "can_a_detailed_quantitative_breakdown_of_systematic_uncertainties_in_neutrino_decay_lifetime_measurements_be_provided_for_each_major_experimental_collaboration.md": (
        "Neutrino Decay Lifetime Limits and Systematic Uncertainties",
        "neutrino_decay_lifetime_limits_and_systematic_uncertainties.md"
    ),
    "can_a_rigorous_model_of_wimp_baryogenesis_be_constructed_that_naturally_satisfies_the_washout_constraint_without_invoking_finetuned_flavor_structures_or_heavy_mass_hierarchies.md": (
        "WIMP Baryogenesis Models and Washout Constraints",
        "wimp_baryogenesis_models_and_washout_constraints.md"
    ),
    "can_independent_laboratory_experiments_definitively_disentangle_activeflux_loss_due_to_invisible_decay_from_flux_normalization_systematic_errors.md": (
        "Disentangling Neutrino Invisible Decay from Flux Normalization Errors",
        "disentangling_neutrino_invisible_decay_from_flux_normalization_errors.md"
    ),
    "can_independent_publicly_available_datasets_from_juno_dune_or_hyperkamiokande_be_released_to_enable_external_verification_of_neutrino_decay_bounds.md": (
        "External Verification of Neutrino Decay Bounds via Open Datasets",
        "external_verification_of_neutrino_decay_bounds_via_open_datasets.md"
    ),
    "can_operator_domain_and_spectral_decomposition_analyses_for_the_nonhermitian_hamiltonian_with_decay_terms_be_rigorously_established.md": (
        "Spectral Decomposition of Non-Hermitian Hamiltonians with Decay Terms",
        "spectral_decomposition_of_non_hermitian_decay_hamiltonians.md"
    ),
    "can_the_mathematical_framework_for_neutrino_decay_survival_probabilities_and_flavor_oscillation_modifications_be_rigorously_revised_and_peerreviewed_to_achieve_full_mathematical_integrity_compliance.md": (
        "Mathematical Formulation of Neutrino Decay Survival Probabilities",
        "mathematical_formulation_of_neutrino_decay_survival_probabilities.md"
    ),
    "can_the_theoretical_predictions_from_quantum_extremal_surface_computations_and_modified_gravity_approaches_be_linked_to_potentially_observable_signatures_eg_in_black_hole_evaporation_or_gravitational_wave_echoes_to_enable_empirical_testing.md": (
        "Observational Signatures of Quantum Extremal Surfaces and Black Hole Evaporation",
        "observational_signatures_of_quantum_extremal_surfaces_and_black_hole_evaporation.md"
    ),
    "can_you_clarify_the_commutation_relations_m__and_provide_the_explicit_calculation_showing_the_convergence_of_the_bch_series_for_your_nonhermitian_effective_hamiltonian.md": (
        "Non-Hermitian Effective Hamiltonian for Neutral-Meson Systems",
        "non_hermitian_effective_hamiltonian_neutral_meson_systems.md"
    ),
    "can_you_provide_a_rigorous_derivationbased_proof_of_the_modified_survival_probability_equations_using_nonhermitian_hamiltonians_and_lindblad_operator_formalism.md": (
        "Modified Neutrino Survival Probabilities and Vacuum Decoherence",
        "modified_neutrino_survival_probabilities_and_vacuum_decoherence.md"
    ),
    "could_a_comprehensive_visual_schematic_of_the_neutrino_decay_experiments_be_produced_and_included_with_future_reports.md": (
        "Experimental Schematics and Layouts for Neutrino Decay Detection",
        "experimental_schematics_for_neutrino_decay_detection.md"
    ),
    "could_the_researchers_provide_simulation_studies_or_sensitivity_analyses_quantifying_the_discovery_potential_and_limits_achievable_with_current_technologies_under_realistic_experimental_conditions.md": (
        "Simulation Studies and Sensitivity Limits for Neutrino Decay Detectors",
        "simulation_studies_and_sensitivity_limits_for_neutrino_decay_detectors.md"
    ),
    "does_the_inclusion_of_dark_acoustic_oscillations_or_dissipation_in_complex_darksector_models_alter_the_largescale_structure_success_of_sidm_compared_to_standard_collisionless_cdm.md": (
        "Dark Acoustic Oscillations and Dissipation in Complex Dark-Sector Models",
        "dark_acoustic_oscillations_and_dissipation_in_dark_sector_models.md"
    ),
    "does_the_inclusion_of_potential_nonstandard_interactions_nsi_in_the_matterevolution_hamiltonian_qualitatively_shift_the_existing_bounds_on_neutrino_decay_lifetimes_at_dune.md": (
        "Non-Standard Interactions and Neutrino Decay Lifetime Bounds at DUNE",
        "non_standard_interactions_and_neutrino_decay_lifetime_bounds_at_dune.md"
    ),
    "given_that_current_observational_constraints_force_both_theories_toward_the_limit_of_gr_what_is_the_minimum_viable_degree_of_modification_that_remains_mathematically_stable_and_physically_motivated_for_either_model.md": (
        "Minimum Viable Modifications to General Relativity",
        "minimum_viable_modifications_to_general_relativity.md"
    ),
    "has_there_been_engagement_with_theoretical_and_experimental_neutrino_physics_collaborations_to_improve_model_consistency_and_empirical_test_strategies_to_move_beyond_purely_theoretical_classification.md": (
        "Collaborative Empirical Test Strategies for Theoretical Neutrino Models",
        "collaborative_empirical_test_strategies_for_neutrino_models.md"
    ),
    "how_can_cosmological_observations_be_refined_to_better_constrain_or_detect_neutrino_decay_signatures.md": (
        "Refining Cosmological Observations for Neutrino Decay Signatures",
        "refining_cosmological_observations_for_neutrino_decay_signatures.md"
    ),
    "how_can_cosmological_observations_be_refined_to_better_discriminate_between_warm_dark_matter_effects_predicted_by_sterile_neutrinos_and_cold_dark_matter_scenarios.md": (
        "Discriminating Warm vs Cold Dark Matter via Cosmological Probes",
        "discriminating_warm_vs_cold_dark_matter_via_cosmological_probes.md"
    ),
    "how_can_hydrodynamic_simulations_be_structured_to_conclusively_break_the_degeneracy_between_baryonic_feedback_effects_and_darksector_physics_sfdm_wave_effects_vs_sidm_collisions_in_dwarf_galaxy_cores.md": (
        "Hydrodynamic Simulations Disentangling Baryonic Feedback from SFDM and SIDM",
        "hydrodynamic_simulations_baryonic_feedback_sfdm_sidm.md"
    ),
    "how_can_sterile_neutrino_production_mechanisms_be_constrained_or_clarified_by_future_neutrino_oscillation_or_cosmological_probes.md": (
        "Sterile Neutrino Production Mechanisms and Cosmological Constraints",
        "sterile_neutrino_production_mechanisms_and_cosmological_constraints.md"
    ),
    "how_can_the_proposed_comparison_between_nearby_steady_astrophysical_sources_and_the_diffuse_neutrino_population_be_statistically_quantified_to_yield_an_unambiguous_test_given_that.md": (
        "Statistical Tests of Point-Source vs Diffuse Astrophysical Neutrinos",
        "statistical_tests_of_point_source_vs_diffuse_astrophysical_neutrinos.md"
    ),
    "how_can_upcoming_astrophysical_neutrino_observatories_enhance_flavor_and_spectral_resolution_to_better_distinguish_neutrino_decay_effects_from_standard_oscillations_or_source_variability.md": (
        "Astrophysical Neutrino Flavor and Spectral Resolution Enhancement",
        "astrophysical_neutrino_flavor_and_spectral_resolution_enhancement.md"
    ),
    "how_do_nonminimal_extensions_or_ultraviolet_completions_of_these_models_affect_their_testability_and_theoretical_robustness_in_light_of_planned_future_experiments.md": (
        "Ultraviolet Completions and Experimental Testability of BSM Physics",
        "uv_completions_and_experimental_testability_of_bsm_models.md"
    ),
    "how_might_ambiguities_in_neutrino_state_definitions_during_decay_be_theoretically_and_experimentally_clarified.md": (
        "Neutrino State Definitions and Asymptotic States During Decay",
        "neutrino_state_definitions_and_asymptotic_decay_states.md"
    ),
    "how_might_future_experiments_or_observations_be_designed_to_effectively_distinguish_between_freezein_and_freezeout_dark_matter_production_mechanisms.md": (
        "Distinguishing Freeze-In and Freeze-Out Dark Matter Mechanisms",
        "distinguishing_freeze_in_and_freeze_out_dark_matter_mechanisms.md"
    ),
    "how_might_potential_degeneracies_in_astrophysical_signals_between_sfdm_phonon_effects_and_alternative_dark_matter_models_be_resolved_observationally.md": (
        "Superfluid Dark Matter Phonon Effects",
        "superfluid_dark_matter_phonon_effects.md"
    ),
    "how_might_the_assumptions_of_fundamental_spacetime_discreteness_or_entanglementgeometry_duality_be_tested_or_challenged_empirically.md": (
        "Empirical Tests of Spacetime Discreteness and Entanglement-Geometry Duality",
        "empirical_tests_of_spacetime_discreteness_and_entanglement_geometry_duality.md"
    ),
    "how_would_a_joint_bayesian_evidence_analysis_significantly_alter_the_current_frequentist_conclusion_that_the_decay_hypothesis_is_only_a_15_fluctuation.md": (
        "Joint Bayesian Evidence Analysis of the Neutrino Decay Hypothesis",
        "bayesian_evidence_analysis_neutrino_decay_hypothesis.md"
    ),
    "to_what_degree_do_current_uncertainties_in_dunes_nuclear_crossmodel_backgrounds_eg_rpa_2p2h_effects_overlap_with_the_energydependent_spectral_distortion_predicted_by_visible_neutrino_decay.md": (
        "DUNE Nuclear Cross-Section Uncertainties vs Visible Neutrino Decay",
        "dune_nuclear_cross_section_uncertainties_vs_visible_neutrino_decay.md"
    ),
    "what_advancements_in_relativistic_modeling_and_numerical_simulations_are_needed_to_more_conclusively_differentiate_sfdm_predictions_from_cdm_scenarios_in_structure_formation.md": (
        "Relativistic Simulations Differentiating SFDM from Lambda-CDM",
        "relativistic_simulations_differentiating_sfdm_from_lambda_cdm.md"
    ),
    "what_advancements_or_new_data_from_upcoming_experiments_could_improve_the_mathematical_modeling_and_strengthen_the_formalism_of_neutrino_decay_constraints.md": (
        "Experimental Advancements in Neutrino Decay Constraints",
        "experimental_advancements_in_neutrino_decay_constraints.md"
    ),
    "what_are_the_implications_of_nonstandard_early_universe_cosmologies_on_the_predicted_relic_abundances_for_freezein_versus_freezeout_models.md": (
        "Non-Standard Early Cosmologies and Dark Matter Relic Abundances",
        "non_standard_early_cosmologies_and_dark_matter_relic_abundances.md"
    ),
    "what_are_the_most_promising_nearfuture_experimental_strategies_to_improve_detection_sensitivity_for_axion_dark_matter_in_the_low_mass_range.md": (
        "Low-Mass Axion Dark Matter Detection Strategies",
        "low_mass_axion_dark_matter_detection_strategies.md"
    ),
    "what_are_the_most_promising_upcoming_observational_or_experimental_tests_that_could_directly_detect_signatures_unique_to_superfluid_dark_matter.md": (
        "Observational Signatures Unique to Superfluid Dark Matter",
        "observational_signatures_unique_to_superfluid_dark_matter.md"
    ),
    "what_are_the_prospects_and_timelines_for_observational_advances_eg_nextgeneration_eht_or_improved_gravitational_wave_detectors_to_resolve_current_degeneracies_between_kerr_and_alternative_black_hole_models.md": (
        "Resolving Kerr vs Alternative Black Hole Degeneracies via Next-Gen Probes",
        "resolving_kerr_vs_alternative_black_hole_degeneracies.md"
    ),
    "what_are_the_prospects_for_constructing_a_quantum_measure_satisfying_all_covariant_and_causality_requirements_in_causal_set_theory.md": (
        "Covariant Quantum Measure Construction in Causal Set Theory",
        "covariant_quantum_measure_construction_in_causal_set_theory.md"
    ),
    "what_concrete_experimental_signatures_could_distinguish_quantum_causal_sets_from_tensor_network_approaches.md": (
        "Experimental Signatures Distinguishing Causal Sets from Tensor Networks",
        "experimental_signatures_distinguishing_causal_sets_from_tensor_networks.md"
    ),
    "what_experimental_advancements_or_novel_observational_signatures_could_most_effectively_distinguish_between_higgs_portal_dark_matter_and_sterile_neutrino_dark_matter_in_the_next_decade.md": (
        "Distinguishing Higgs Portal from Sterile Neutrino Dark Matter",
        "distinguishing_higgs_portal_from_sterile_neutrino_dark_matter.md"
    ),
    "what_experimental_advances_are_required_to_unambiguously_distinguish_neutrino_decay_effects_from_oscillation_nsi_and_decoherence_effects.md": (
        "Disentangling Neutrino Decay from NSI and Environmental Decoherence",
        "disentangling_neutrino_decay_from_nsi_and_decoherence.md"
    ),
    "what_experimental_collaborations_could_provide_the_latest_bounds_or_evidence_relevant_to_neutrino_decay.md": (
        "Experimental Collaboration Bounds on Neutrino Decay",
        "experimental_collaboration_bounds_on_neutrino_decay.md"
    ),
    "what_experimental_designs_or_data_analyses_can_definitively_distinguish_neutrino_decay_effects_from_alternative_damping_mechanisms_such_as_decoherence_or_nonstandard_interactions.md": (
        "Distinguishing Neutrino Decay from Damping and Decoherence Mechanisms",
        "distinguishing_neutrino_decay_from_damping_and_decoherence.md"
    ),
    "what_experimental_evidence_or_signatures_would_decisively_distinguish_neutrino_decay_from_sterile_neutrino_or_nonstandard_interaction_scenarios.md": (
        "Signatures Distinguishing Neutrino Decay from Sterile Neutrino Scenarios",
        "signatures_distinguishing_neutrino_decay_from_sterile_neutrinos.md"
    ),
    "what_future_experimental_technologies_or_techniques_could_realistically_reduce_the_uncertainties_in_nuclear_matrix_elements_impacting_neutrinoless_double_beta_decay_analyses.md": (
        "Reducing Nuclear Matrix Element Uncertainties in 0vbb Decay",
        "reducing_nuclear_matrix_element_uncertainties_in_0vbb_decay.md"
    ),
    "what_novel_detector_designs_might_improve_sensitivity_to_spectral_distortions_near_beta_decay_endpoints_beyond_current_capabilities_like_katrin.md": (
        "Next-Generation Beta Decay Endpoint Spectrometry Beyond KATRIN",
        "next_generation_beta_decay_endpoint_spectrometry.md"
    ),
    "what_progress_has_been_made_in_extending_tensor_network_methods_to_fully_dynamical_lorentzian_spacetimes_reproducing_classical_gravity.md": (
        "Tensor Networks in Dynamical Lorentzian Spacetimes",
        "tensor_networks_in_dynamical_lorentzian_spacetimes.md"
    ),
    "what_specific_experimental_observables_or_signatures_can_uniquely_discriminate_neutrino_decay_from_background_processes_and_alternative_new_physics_scenarios_in_dune_juno_or_icecube_datasets.md": (
        "Unique Observables for Neutrino Decay in Major Detectors",
        "unique_observables_for_neutrino_decay_in_major_detectors.md"
    ),
    "what_specific_experimental_signature_could_unambiguously_differentiate_a_screeningprotected_scalar_field_from_a_nonlocal_interaction_in_the_context_of_strongfield_gravity_eg_binary_black_hole_mergers.md": (
        "Screening-Protected Scalar Fields vs Non-Local Gravity in Black Hole Mergers",
        "screening_protected_scalar_fields_vs_non_local_gravity.md"
    ),
    "what_specific_experimental_strategies_are_most_promising_for_achieving_direct_detection_of_neutrino_decay.md": (
        "Direct Detection Strategies for Neutrino Decay",
        "direct_detection_strategies_for_neutrino_decay.md"
    ),
    "what_specific_experimental_thresholds_in_nextgeneration_skipperccd_or_subgev_dark_matter_detectors_are_required_to_provide_a_meaningful_falsification_test_for_the_5_gev_adm_mass_sc.md": (
        "5 GeV Asymmetric Dark Matter Mass Scale and Skipper-CCD Constraints",
        "five_gev_asymmetric_dark_matter_skipper_ccd_constraints.md"
    ),
    "what_specific_laboratorybased_experiment_such_as_an_axion_haloscope_or_lightmediator_search_could_definitively_falsify_the_most_plausible_variants_of_sidm_or_sfdm.md": (
        "Laboratory Haloscope and Light-Mediator Tests of SIDM and SFDM",
        "laboratory_tests_of_sidm_and_sfdm_variants.md"
    ),
    "what_specific_mathematical_or_conceptual_gaps_prevent_the_quantum_sequential_growth_process_from_being_fully_formulated.md": (
        "Quantum Sequential Growth (QSG) Process in Causal Set Cosmology",
        "quantum_sequential_growth_process_in_causal_set_cosmology.md"
    ),
    "what_specific_nonmarkovian_memory_kernels_would_arise_if_neutrino_propagation_through_earths_matter_density_is_treated_as_a_truly_nonadiabatic_process.md": (
        "Non-Markovian Memory Kernels in Non-Adiabatic Neutrino Matter Propagation",
        "non_markovian_memory_kernels_in_neutrino_matter_propagation.md"
    ),
    "what_specific_numerical_benchmarks_or_simulations_can_be_performed_to_enhance_the_mathematical_integrity_verification_of_neutrino_decay_effects_in_cosmological_boltzmann_codes.md": (
        "Numerical Benchmarks for Neutrino Decay in Cosmological Boltzmann Codes",
        "numerical_benchmarks_for_neutrino_decay_in_boltzmann_codes.md"
    ),
    "what_specific_operatortheoretic_proofs_can_be_developed_to_ensure_full_mathematical_integrity_compliance_of_the_neutrino_decay_survival_probability_framework.md": (
        "Operator-Theoretic Foundations of Neutrino Decay Survival Probabilities",
        "operator_theoretic_foundations_of_neutrino_decay.md"
    ),
    "what_steps_can_be_taken_to_integrate_higherorder_effects_and_nonstandard_interactions_consistently_within_the_existing_framework.md": (
        "Integrating Higher-Order Effects and Non-Standard Interactions in Neutrino Dynamics",
        "higher_order_effects_and_non_standard_interactions_in_neutrino_dynamics.md"
    ),
    "which_observational_strategies_or_novel_crosscorrelation_methods_could_most_effectively_break_degeneracies_between_neutrino_decay_signatures_and_other_neutrino_property_variations_in_upcoming_surveys.md": (
        "Cross-Correlation Methods Breaking Degeneracies in Neutrino Decay Surveys",
        "cross_correlation_methods_breaking_neutrino_decay_degeneracies.md"
    ),
    "which_open_questions_and_potential_falsification_tests_should_be_prioritized_to_move_the_framework_towards_empirical_verification.md": (
        "Empirical Falsification Priorities for Theoretical Physics Extensions",
        "empirical_falsification_priorities_for_theoretical_physics.md"
    ),
    "will_you_perform_a_complete_dimensional_analysis_table_for_your_proposed_modified_survival_equations_showing_explicit_si_unit_tracing_to_prove_they_are_dimensionless.md": (
        "Dimensional Analysis and Unit Tracing of Modified Survival Equations",
        "dimensional_analysis_and_unit_tracing_of_modified_survival_equations.md"
    ),
    "will_you_provide_a_statistical_chisquared_fit_analysis_comparing_your_proposed_modifications_against_contemporary_datasets_from_t2k_nova_or_icecube.md": (
        "Statistical Chi-Squared Fit Analysis for BSM Neutrino Physics",
        "statistical_chi_squared_fit_analysis_bsm_neutrino_physics.md"
    ),
    "can_integrated_information_theory_iit_be_formalized_within_spacetime_geometry_to_address_the_hard_problem_of_consciousness.md": (
        "Formalizing Integrated Information Theory (IIT) within Spacetime Geometry",
        "formalizing_integrated_information_theory_within_spacetime_geometry.md"
    )
}


def backup_knowledge_base(repo_root: Path) -> Path:
    """Creates a full timestamped backup of the level_1 and level_3 folders before making changes."""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = repo_root / "knowledge_base" / "logs" / f"kb_backup_{ts}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    l1_dir = repo_root / "knowledge_base" / "level_1_fundamental_physics"
    l3_dir = repo_root / "knowledge_base" / "level_3_emergence_and_intelligence"
    
    if l1_dir.exists():
        shutil.copytree(l1_dir, backup_dir / "level_1_fundamental_physics")
    if l3_dir.exists():
        shutil.copytree(l3_dir, backup_dir / "level_3_emergence_and_intelligence")
        
    print(f"[*] Created knowledge base backup at: {backup_dir}")
    return backup_dir


def update_markdown_headers(file_path: Path, new_title: str):
    """Updates YAML frontmatter title and first # heading in a markdown file."""
    text = file_path.read_text(encoding="utf-8")
    
    # Update frontmatter title
    def replace_fm_title(match):
        fm = match.group(1)
        new_lines = []
        replaced = False
        for line in fm.splitlines():
            if line.strip().lower().startswith("title:"):
                # preserve quotes style
                new_lines.append(f'title: "{new_title}"')
                replaced = True
            else:
                new_lines.append(line)
        if not replaced:
            new_lines.insert(0, f'title: "{new_title}"')
        return "---\n" + "\n".join(new_lines) + "\n---"

    text = re.sub(r"^---\s*\n([\s\S]*?)\n---", replace_fm_title, text, count=1)
    
    # Update top-level # heading
    text = re.sub(r"^#\s+.*$", f"# {new_title}", text, count=1, flags=re.MULTILINE)
    
    file_path.write_text(text, encoding="utf-8")


def run_consolidation(dry_run: bool = True):
    print("=" * 70)
    print(f"KNOWLEDGE BASE CONSOLIDATION (Mode: {'DRY RUN' if dry_run else 'APPLY'})")
    print("=" * 70)
    
    kb_dir = REPO_ROOT / "knowledge_base"
    l1_dir = kb_dir / "level_1_fundamental_physics"
    l3_dir = kb_dir / "level_3_emergence_and_intelligence"
    archive_dir = kb_dir / "archive" / "legacy_meta_reviews"
    
    if not dry_run:
        backup_knowledge_base(REPO_ROOT)
        archive_dir.mkdir(parents=True, exist_ok=True)
        
    # 1. Process Meta-Files (Archive)
    print("\n[PHASE 1] Archiving Meta-Review Question Files:")
    archived_count = 0
    for meta_fn in sorted(META_FILES):
        src_path = l1_dir / meta_fn
        dest_path = archive_dir / meta_fn
        if src_path.exists():
            archived_count += 1
            if dry_run:
                print(f"  [DRY RUN ARCHIVE] {meta_fn} -> archive/legacy_meta_reviews/")
            else:
                shutil.move(str(src_path), str(dest_path))
                print(f"  [ARCHIVED] {meta_fn} -> archive/legacy_meta_reviews/")
        else:
            print(f"  [SKIP] Not found: {meta_fn}")
            
    print(f"Total meta-review files to archive: {archived_count}")
    
    # 2. Process Curated Renames
    print("\n[PHASE 2] Renaming & Retitling Scientific Research Files:")
    renamed_count = 0
    for old_fn, (new_title, new_fn) in CURATED_RENAMES.items():
        folder = l3_dir if "level_3" in old_fn or old_fn.startswith("can_integrated") else l1_dir
        src_path = folder / old_fn
        dest_path = folder / new_fn
        
        if src_path.exists():
            renamed_count += 1
            if dry_run:
                print(f"  [DRY RUN RENAME]")
                print(f"    Old: {old_fn}")
                print(f"    New: {new_fn}")
                print(f"    Title: \"{new_title}\"")
            else:
                # Rename the file
                src_path.rename(dest_path)
                # Update frontmatter and top heading
                update_markdown_headers(dest_path, new_title)
                print(f"  [RENAMED & RETITLED] {new_fn} (\"{new_title}\")")
        else:
            print(f"  [SKIP] Not found: {old_fn}")
            
    print(f"Total scientific research files to rename: {renamed_count}")
    
    # 3. Synchronize Index & Database
    if not dry_run:
        print("\n[PHASE 3] Synchronizing Knowledge Base Index & Graph...")
        try:
            from index_utils import synchronize_index
        except ImportError:
            from src.index_utils import synchronize_index
            
        synchronize_index("knowledge_base/_index.md", REPO_ROOT)
        print("[*] Rebuilt knowledge_base/_index.md and knowledge_base/database.json")
        
        # Check equation archaeologist if available
        try:
            from equation_archaeologist import EquationArchaeologist
            EquationArchaeologist(REPO_ROOT).run()
            print("[*] Synchronized Equation Archaeologist")
        except Exception as eq_err:
            print(f"[!] Equation Archaeologist notice: {eq_err}")
            
    print("\n" + "=" * 70)
    if dry_run:
        print("DRY RUN COMPLETE. Run with --apply to execute the changes.")
    else:
        print("CONSOLIDATION APPLIED SUCCESSFULLY.")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Consolidate legacy question-titled markdown files in knowledge base.")
    parser.add_argument("--apply", action="store_true", help="Apply the renames, moves, and index rebuild.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files.")
    args = parser.parse_args()
    
    dry_run = not args.apply
    run_consolidation(dry_run=dry_run)


if __name__ == "__main__":
    main()
