Change History
=============
Note these changes related to eyeballing strategy rather than focusing on the GH cide since
the history of the latter is recorded in the commit history.

VRA 1.1 - Upcoming
   - day N feature ``DET_mag_median`` added back in. Marginal gains but also consistent with keeping ``NON_mag_median`` and removing both is worse.

VRA 1.0 - 2025-02-03
   - VRA real and galactic models trained on the Duck data-set. Ranges from 27-03-2024 to 22-01-2025
   - The following day1 features were pruned: `SN``, ``ORPHAN``, ``NT``, ``UNCLEAR``
   - The following dayN features were pruned: ``SN``, ``ORPHAN``, ``NT``, ``UNCLEAR``, ``DET_N_today``, ``NON_N_today``, ``DET_mag_median``
   - Eyeballing now split into extragalactic and galactic
   - Eyeball list now named extragalactic candidate list (although purgatory objects still linger at the bottom of that list)
   - Extra galactic candidates defined as rank > 7.5 (instead of 4)
   - Galactic candidates defined as within 0.45 of the top right corner of score space (fudge-factor = 1 instead of 0.4)
   - ScoreAndRank now has the is_gal_cand property (boolean flag)
   - Auto-garbaging strategy modified: day1: max_rank <1 (was 1.5), day2: max_rank < 2 (was 3), day3+ : mean_rank <3 (unchanged).
   - Number of alerts reported by slack-bot no longer overestimated
   - el01z weekly reports and purgatory sentinel now run on the ATLAS server (Fridays)
   - TNS cross-matching to garbage list done weekly on Friday mornings

VRA beta0.1  - 2024-12-06
   - VRA real and galactic models trained on the Crabby data-set. Ranges from 27-03-2024 to 13-08-2024
   - Fudge-factor changed to 0.4 (from 0.5)