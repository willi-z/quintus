use crate::material::Material;
use nalgebra as na;

pub enum ViewSystem {
    Local,
    Global,
}

pub struct Ply {
    pub material: Material,
    pub thickness: f64,
    pub rotation_in_rad: f64,
}

impl Ply {
    pub fn new(material: Material, thickness: f64, rotation_in_rad: f64) -> Self {
        Self {
            material: material,
            thickness: thickness,
            rotation_in_rad: rotation_in_rad,
        }
    }
    pub fn rotate(&self, rotation_in_rad: f64) -> Self {
        Self {
            material: self.material.clone(),
            thickness: self.thickness,
            rotation_in_rad: self.rotation_in_rad + rotation_in_rad,
        }
    }

    pub fn get_stiffness(&self, view: ViewSystem) -> na::SMatrix<f64, 3, 3> {
        match view {
            ViewSystem::Local => return self.material.get_plane_strain_stiffness(),
            ViewSystem::Global => {
                let c = self.rotation_in_rad.cos();
                let s = self.rotation_in_rad.sin();

                let t_sigma = na::SMatrix::<f64, 3, 3>::new(
                    c.powi(2),
                    s.powi(2),
                    -2.0 * s * c,
                    s.powi(2),
                    c.powi(2),
                    2.0 * s * c,
                    s * c,
                    -s * c,
                    c.powi(2) - s.powi(2),
                );

                let t_sigma_t = na::SMatrix::<f64, 3, 3>::new(
                    c.powi(2),
                    s.powi(2),
                    s * c,
                    s.powi(2),
                    c.powi(2),
                    -s * c,
                    -2.0 * s * c,
                    2.0 * s * c,
                    c.powi(2) - s.powi(2),
                );

                return t_sigma * self.material.get_plane_strain_stiffness() * t_sigma_t;
            }
        }
    }

    pub fn get_local_stress(&self, stress: na::SVector<f64, 3>) -> na::SVector<f64, 3> {
        let c = self.rotation_in_rad.cos();
        let s = self.rotation_in_rad.sin();

        let t_sigma_inv = na::SMatrix::<f64, 3, 3>::new(
            c.powi(2),
            s.powi(2),
            2.0 * c * s,
            s.powi(2),
            c.powi(2),
            -2.0 * c * s,
            -c * s,
            c * s,
            c.powi(2) - s.powi(2),
        );

        t_sigma_inv * stress
    }

    pub fn get_local_strain(&self, strain: na::SVector<f64, 3>) -> na::SVector<f64, 3> {
        let c = self.rotation_in_rad.cos();
        let s = self.rotation_in_rad.sin();

        let t_epsilon_inv = na::SMatrix::<f64, 3, 3>::new(
            c.powi(2),
            s.powi(2),
            c * s,
            s.powi(2),
            c.powi(2),
            -c * s,
            -2.0 * c * s,
            2.0 * c * s,
            c.powi(2) - s.powi(2),
        );

        t_epsilon_inv * strain
    }
}

pub enum PlyOrdering {
    TopToBot,
    BotToTop,
}

pub struct Stackup {
    pub plies: Vec<Ply>,
    pub thickness: f64,
    pub abd: na::SMatrix<f64, 6, 6>,
    pub density: Option<f64>,
}

impl Stackup {
    pub fn new(mut plies: Vec<Ply>, ply_ordering: PlyOrdering) -> Self {
        match ply_ordering {
            PlyOrdering::TopToBot => plies.reverse(),
            _ => (),
        }

        let mut stackup = Self {
            plies,
            thickness: 0.0,
            density: None,
            abd: na::SMatrix::<f64, 6, 6>::zeros(),
        };
        stackup.thickness = stackup.calc_thickness();
        stackup.abd = stackup.calc_abd();
        stackup
    }

    pub fn calc_thickness(&self) -> f64 {
        self.plies.iter().map(|ply| ply.thickness).sum()
    }

    pub fn calc_density(&self) -> Option<f64> {
        // Check if any ply's material density is None
        if self.plies.iter().any(|ply| ply.material.density.is_none()) {
            return None;
        }

        // Perform the density calculation if all densities are Some
        let thick_density: f64 = self
            .plies
            .iter()
            .map(|ply| ply.thickness * ply.material.density.unwrap())
            .sum();

        Some(thick_density / self.thickness)
    }

    pub fn rotate(&self, angle: f64, degree: bool) -> Self {
        let rad_angle = if degree { angle.to_radians() } else { angle };
        let plies: Vec<Ply> = self.plies.iter().map(|ply| ply.rotate(rad_angle)).collect();
        Stackup::new(plies, PlyOrdering::BotToTop)
    }

    #[rustfmt::skip]
    pub fn calc_abd(&self) -> na::SMatrix<f64, 6, 6> {
        let h = self.thickness / 2.0;

        let mut mat_a = na::SMatrix::<f64, 3, 3>::zeros();
        let mut mat_b = na::SMatrix::<f64, 3, 3>::zeros();
        let mut mat_d = na::SMatrix::<f64, 3, 3>::zeros();
        let mut z_bot = -h;

        for ply in &self.plies {
            let z_top = z_bot + ply.thickness;
            let q_bar = ply.get_stiffness(ViewSystem::Global);
            mat_a += q_bar * (z_top - z_bot);
            mat_b += 0.5 * q_bar * (z_top.powi(2) - z_bot.powi(2));
            mat_d += (1.0 / 3.0) * q_bar * (z_top.powi(3) - z_bot.powi(3));
            z_bot = z_top;
        }

        return na::SMatrix::<f64, 6, 6>::new(
            mat_a[(0, 0)], mat_a[(0, 1)], mat_a[(0, 2)], mat_b[(0, 0)], mat_b[(0, 1)], mat_b[(0, 2)],
            mat_a[(1, 0)], mat_a[(1, 1)], mat_a[(1, 2)], mat_b[(1, 0)], mat_b[(1, 1)], mat_b[(1, 2)],
            mat_a[(2, 0)], mat_a[(2, 1)], mat_a[(2, 2)], mat_b[(2, 0)], mat_b[(2, 1)], mat_b[(2, 2)],
            mat_b[(0, 0)], mat_b[(0, 1)], mat_b[(0, 2)], mat_d[(0, 0)], mat_d[(0, 1)], mat_d[(0, 2)],
            mat_b[(1, 0)], mat_b[(1, 1)], mat_b[(1, 2)], mat_d[(1, 0)], mat_d[(1, 1)], mat_d[(1, 2)],
            mat_b[(2, 0)], mat_b[(2, 1)], mat_b[(2, 2)], mat_d[(2, 0)], mat_d[(2, 1)], mat_d[(2, 2)],
        );
    }

    pub fn apply_load(&self, mech_load: na::SVector<f64, 6>) -> na::SVector<f64, 6> {
        let inv_abd = self
            .abd
            .try_inverse()
            .expect("ABD matrix must be invertible");
        inv_abd * mech_load
    }

    pub fn apply_deformation(&self, deformation: na::SVector<f64, 6>) -> na::SVector<f64, 6> {
        self.abd * deformation
    }

    pub fn get_strains(
        &self,
        deformation: na::SVector<f64, 6>,
    ) -> Vec<(na::SVector<f64, 3>, na::SVector<f64, 3>)> {
        let h = self.thickness / 2.0;
        let strain_membrane = deformation.fixed_rows::<3>(0).into_owned();
        let curvature = deformation.fixed_rows::<3>(3).into_owned();

        let mut strains = Vec::new();
        let mut z_bot = -h;

        for ply in &self.plies {
            let z_top = z_bot + ply.thickness;
            let strain_top = strain_membrane + z_top * curvature;
            let strain_bot = strain_membrane + z_bot * curvature;

            let strain_lt_top = ply.get_local_strain(strain_top);
            let strain_lt_bot = ply.get_local_strain(strain_bot);

            strains.push((strain_lt_bot, strain_lt_top));
            z_bot = z_top;
        }

        strains
    }

    pub fn get_stresses(
        &self,
        strains: Vec<(na::SVector<f64, 3>, na::SVector<f64, 3>)>,
    ) -> Vec<(na::SVector<f64, 3>, na::SVector<f64, 3>)> {
        let mut stresses = Vec::new();

        for i in 0..self.plies.len() {
            let (strain_lt_bot, strain_lt_top) = strains[i];

            let stiffness = self.plies[i].get_stiffness(ViewSystem::Local); // Assuming get_stiffness() handles local=True
            let stress_lt_top = stiffness * strain_lt_top;
            let stress_lt_bot = stiffness * strain_lt_bot;

            stresses.push((stress_lt_bot, stress_lt_top));
        }

        stresses
    }

    pub fn calc_homogenized(&self) -> Material {
        let scale = 1.0 / self.thickness;
        let abd = self.abd;
        let em_ll = scale * (abd[(0, 0)] - abd[(0, 1)].powi(2) / abd[(1, 1)]);
        let em_tt = scale * (abd[(1, 1)] - abd[(0, 1)].powi(2) / abd[(0, 0)]);
        let g_lt = scale * abd[(2, 2)];
        let nu_lt = abd[(0, 1)] / abd[(1, 1)];
        Material::TransverselyIsotropic(em_ll, em_tt, nu_lt, g_lt, Option::None, self.density)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use nalgebra::{self as na, SMatrix, SVector};

    fn get_significance(number: f64) -> i32 {
        if number != 0.0 {
            let significance = number.abs().log10().ceil().abs() as i32;
            significance
        } else {
            0
        }
    }

    fn round_to_nth_digit(value: f64, n: i32) -> f64 {
        let multiplier = 10f64.powi(n);
        (value * multiplier).round() / multiplier
    }

    #[test]
    fn test_abd_a() {
        let material = Material::TransverselyIsotropic(141000.0, 9340.0, 0.35, 4500.0, None, None);

        let test_cases: Vec<(Vec<Ply>, SMatrix<f64, 3, 3>)> = vec![
            (
                vec![Ply::new(material.clone(), 1.0, 0.0)],
                na::SMatrix::from_row_slice(&[
                    142153.5, 3295.7, 0.0, 3295.7, 9416.4, 0.0, 0.0, 0.0, 4500.0,
                ]),
            ),
            (
                vec![Ply::new(material.clone(), 1.0, 45.0_f64.to_radians())],
                na::SMatrix::from_row_slice(&[
                    44040.4, 35040.4, 33184.3, 35040.4, 44040.4, 33184.3, 33184.3, 33184.3, 36244.6,
                ]),
            ),
            (
                vec![Ply::new(material.clone(), 1.0, -45.0_f64.to_radians())],
                na::SMatrix::from_row_slice(&[
                    44040.4, 35040.4, -33184.3, 35040.4, 44040.4, -33184.3, -33184.3, -33184.3,
                    36244.6,
                ]),
            ),
        ];

        for (plies, a_mat) in test_cases {
            let stackup = Stackup::new(plies, PlyOrdering::BotToTop);
            let abd = stackup.abd;
            for i in 0..3 {
                for j in 0..3 {
                    assert!((abd[(i, j)] - a_mat[(i, j)]).abs() < 0.1);
                }
            }
        }
    }

    #[test]
    fn test_abd_b() {
        let material = Material::TransverselyIsotropic(141000.0, 9340.0, 0.35, 4500.0, None, None);

        let test_cases: Vec<(Vec<Ply>, SMatrix<f64, 3, 3>)> = vec![
            (
                vec![Ply::new(material.clone(), 1.0, 0.0)],
                na::SMatrix::from_row_slice(&[
                    11846.1, 274.6, 0.0, 274.6, 784.7, 0.0, 0.0, 0.0, 375.0,
                ]),
            ),
            (
                vec![Ply::new(material.clone(), 1.0, 45.0_f64.to_radians())],
                na::SMatrix::from_row_slice(&[
                    3670.0, 2920.0, 2765.4, 2920.0, 3670.0, 2765.4, 2765.4, 2765.4, 3020.4,
                ]),
            ),
            (
                vec![Ply::new(material.clone(), 1.0, -45.0_f64.to_radians())],
                na::SMatrix::from_row_slice(&[
                    3670.0, 2920.0, -2765.4, 2920.0, 3670.0, -2765.4, -2765.4, -2765.4, 3020.4,
                ]),
            ),
        ];

        for (plies, b_mat) in test_cases {
            let stackup = Stackup::new(plies, PlyOrdering::BotToTop);
            let abd = stackup.abd;
            for i in 3..6 {
                for j in 3..6 {
                    assert!((abd[(i, j)] - b_mat[(i - 3, j - 3)]).abs() < 0.1);
                }
            }
        }
    }

    #[test]
    fn test_deformations() {
        let material = Material::TransverselyIsotropic(141000.0, 9340.0, 0.35, 4500.0, None, None);

        let test_cases: Vec<(Vec<Ply>, SVector<f64, 6>, SVector<f64, 6>)> = vec![
            (
                vec![Ply::new(material.clone(), 1.0, 45.0_f64.to_radians())],
                na::SVector::from_row_slice(&[1.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
                na::SVector::from_row_slice(&[0.000083, -0.000028, -0.00005, 0.0, 0.0, 0.0]),
            ),
            (
                vec![Ply::new(material.clone(), 1.0, -45.0_f64.to_radians())],
                na::SVector::from_row_slice(&[1.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
                na::SVector::from_row_slice(&[0.000083, -0.000028, 0.00005, 0.0, 0.0, 0.0]),
            ),
        ];

        for (plies, loading, deformations) in test_cases {
            let stackup = Stackup::new(plies, PlyOrdering::BotToTop);
            let deform = stackup.apply_load(loading);
            assert_eq!(deform.len(), deformations.len());
            for i in 0..deformations.len() {
                let significance = get_significance(deformations[i]);
                assert_eq!(
                    round_to_nth_digit(deform[i], significance + 2),
                    deformations[i]
                );
            }
        }
    }

    #[test]
    #[rustfmt::skip]
    fn test_strains() {
        let material = Material::TransverselyIsotropic(141000.0, 9340.0, 0.35, 4500.0, None, None);

        let cases = vec![
            (
                vec![Ply::new(material.clone(), 1.0, 45.0f64.to_radians())],
                vec![1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                vec![(
                    vec![2.3e-06, 5.2e-05, -1.1e-04], 
                    vec![2.3e-06, 5.2e-05, -1.1e-04],
                )],
            ),
            (
                vec![Ply::new(material.clone(), 1.0, -45.0f64.to_radians())],
                vec![1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                vec![(
                    vec![2.3e-06, 5.2e-05, 1.1e-04], 
                    vec![2.3e-06, 5.2e-05, 1.1e-04],
                )],
            ),
        ];

        for (plies, loading, strains) in cases {
            let stackup = Stackup::new(plies, PlyOrdering::BotToTop); // Modify the constructor as needed
            let deform = stackup.apply_load(na::SVector::from_vec(loading));
            let layer_strains = stackup.get_strains(deform);

            assert_eq!(layer_strains.len(), strains.len());

            for i in 0..strains.len() {
                let stress = &strains[i].0;
                for j in 0..stress.len() {
                    let significance = get_significance(stress[j]) as i32;
                    assert_eq!(
                        round_to_nth_digit(layer_strains[i].1[j], significance + 2),
                        stress[j]
                    );
                }
                let stress = &strains[i].1;
                for j in 0..stress.len() {
                    let significance = get_significance(stress[j]) as i32;
                    assert_eq!(
                        round_to_nth_digit(layer_strains[i].1[j], significance + 2),
                        stress[j]
                    );
                }
            }
        }
    }

    #[test]
    fn test_stresses() {
        let material = Material::TransverselyIsotropic(141000.0, 9340.0, 0.35, 4500.0, None, None);

        let cases = vec![
            (
                vec![Ply::new(material.clone(), 1.0, 45.0f64.to_radians())],
                vec![1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                vec![(vec![0.5, 0.5, -0.5], vec![0.5, 0.5, -0.5])],
            ),
            (
                vec![Ply::new(material.clone(), 1.0, -45.0f64.to_radians())],
                vec![1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                vec![(vec![0.5, 0.5, 0.5], vec![0.5, 0.5, 0.5])],
            ),
        ];

        for (plies, loading, stresses) in cases {
            let stackup = Stackup::new(plies, PlyOrdering::BotToTop); // Modify the constructor as needed
            let deform = stackup.apply_load(na::SVector::from_vec(loading));
            let layer_strains = stackup.get_strains(deform);
            let layer_stresses = stackup.get_stresses(layer_strains);

            assert_eq!(layer_stresses.len(), stresses.len());

            for i in 0..stresses.len() {
                let stress = &stresses[i].0;
                for j in 0..stress.len() {
                    let significance = get_significance(stress[j]) as i32;
                    assert_eq!(
                        round_to_nth_digit(layer_stresses[i].1[j], significance + 1),
                        stress[j]
                    );
                }
                let stress = &stresses[i].1;
                for j in 0..stress.len() {
                    let significance = get_significance(stress[j]) as i32;
                    assert_eq!(
                        round_to_nth_digit(layer_stresses[i].1[j], significance + 1),
                        stress[j]
                    );
                }
            }
        }
    }
}
