data{
    int N_obs;
    int N_wo;
    int N_author;
    int N_paper;
    int word_id[N_obs];
    int paper_id[N_obs];
    int author_id[N_obs];
}

parameters{
   vector[N_wo] wo_z;
   real<lower=0> sigma_wo;

   matrix[N_wo,N_paper] wo_paper_z;
   vector<lower=0>[N_wo] sigma_wo_paper;
   cholesky_factor_corr[N_wo] L_wo_paper;

   matrix[N_wo,N_author] wo_author_z;
   vector<lower=0>[N_wo] sigma_wo_author;
   cholesky_factor_corr[N_wo] L_wo_author;
}

transformed parameters{
   vector[N_wo] wo_v;
   matrix[N_paper,N_wo] wo_paper_v;
   matrix[N_author,N_wo] wo_author_v;

   wo_v = wo_z * sigma_wo;

   wo_paper_v = (diag_pre_multiply(sigma_wo_paper, L_wo_paper) * wo_paper_z)';
   wo_author_v = (diag_pre_multiply(sigma_wo_author, L_wo_author) * wo_author_z)';
}

model{
    // set priors
    wo_z ~ std_normal();
    to_vector(wo_paper_z)  ~ std_normal();
    to_vector(wo_author_z)  ~ std_normal();
    sigma_wo ~ exponential(1);
    sigma_wo_paper ~ exponential(1);
    sigma_wo_author ~ exponential(1);
    L_wo_paper ~ lkj_corr_cholesky(2);
    L_wo_author ~ lkj_corr_cholesky(2);

    for (i in 1:N_obs) {
        vector[N_wo] soft_p;

        for (w in 1:N_wo) {
            soft_p[w] = wo_v[w] + wo_paper_v[paper_id[i],w] + wo_author_v[author_id[i],w];
        }

        word_id[i] ~ categorical_logit(soft_p);
    }

}

generated quantities {
   matrix[N_wo,N_wo] Rho_author; // recover the author-level correlations between words
   Rho_author = L_wo_author * L_wo_author';
}
