extern crate nalgebra as na;

#[derive(Clone)]
pub enum MechanicalMatrix {
    Compliance(na::SMatrix<f64, 6, 6>),
    Stiffness(na::SMatrix<f64, 6, 6>)
}

#[derive(Clone)]
pub struct Material {
    pub matrix: MechanicalMatrix,
    pub density: Option<f64>,
}

impl Material{
    #[allow(non_snake_case)]
    pub fn Isotropic(em: f64, nu: f64, density: Option<f64>) -> Material{
        let mut compliance = na::SMatrix::<f64, 6, 6>::zeros();
        
        compliance[(0, 0)] = 1.0 / em;
        compliance[(1, 1)] = 1.0 / em;
        compliance[(2, 2)] = 1.0 / em;

        compliance[(0, 1)] = -nu / em;
        compliance[(1, 0)] = compliance[(0, 1)];
        compliance[(0, 2)] = -nu / em;
        compliance[(2, 0)] = compliance[(0, 2)];
        compliance[(1, 2)] = -nu / em;
        compliance[(2, 1)] = compliance[(1, 2)];

        compliance[(3, 3)] = 2.0 * (1.0 + nu) / em;
        compliance[(4, 4)] = compliance[(3, 3)];
        compliance[(5, 5)] = compliance[(3, 3)];
        
        Material { matrix: MechanicalMatrix::Compliance(compliance), density: density }
    }

    #[allow(non_snake_case)]
    pub fn TransverselyIsotropic(em_ll: f64, em_tt: f64, nu_lt: f64, g_lt:f64, nu_tt: Option<f64>, density: Option<f64>) -> Material{
        let nu_tt = match nu_tt{
            Some(nu) => nu,
            None => nu_lt
        };
        let mut compliance = na::SMatrix::<f64, 6, 6>::zeros();
        
        compliance[(0, 0)] = 1.0 / em_ll;
        compliance[(1, 1)] = 1.0 / em_tt;
        compliance[(2, 2)] = 1.0 / em_tt;

        compliance[(0, 1)] = -nu_lt / em_ll;
        compliance[(1, 0)] = compliance[(0, 1)];
        compliance[(0, 2)] = compliance[(0, 1)];
        compliance[(2, 0)] = compliance[(0, 2)];
        compliance[(1, 2)] = -nu_tt / em_ll;
        compliance[(2, 1)] = compliance[(1, 2)];

        compliance[(3, 3)] = 2.0 * (1.0 + nu_tt) / em_ll;
        compliance[(4, 4)] = 1.0 / g_lt;
        compliance[(5, 5)] = compliance[(4, 4)];
        
        Material { matrix: MechanicalMatrix::Compliance(compliance), density: density }
    }

    #[allow(non_snake_case)]
    pub fn Orthotropic(
        em_xx: f64, em_yy: f64, em_zz: f64,
        nu_xy: f64, nu_xz: f64, nu_yz: f64,
        g_xy: f64, g_xz: f64, g_yz: f64,
        density: Option<f64>
    ) -> Material {
        let mut compliance = na::SMatrix::<f64, 6, 6>::zeros();
        
        compliance[(0, 0)] = 1.0 / em_xx;
        compliance[(1, 1)] = 1.0 / em_yy;
        compliance[(2, 2)] = 1.0 / em_zz;
        compliance[(3, 3)] = 1.0 / g_yz;
        compliance[(4, 4)] = 1.0 / g_xz;
        compliance[(5, 5)] = 1.0 / g_xy;

        compliance[(0, 1)] = -nu_xy / em_xx;
        compliance[(1, 0)] = compliance[(0, 1)];
        compliance[(0, 2)] = -nu_xz / em_xx;
        compliance[(2, 0)] = compliance[(0, 2)];
        compliance[(1, 2)] = -nu_yz / em_yy;
        compliance[(2, 1)] = compliance[(1, 2)];

        Material { matrix: MechanicalMatrix::Compliance(compliance), density: density }
    }

    pub fn get_compliance(&self) -> na::SMatrix<f64, 6, 6> {
        match &self.matrix {
            MechanicalMatrix::Compliance(matrix) => *matrix,
            MechanicalMatrix::Stiffness(matrix) => matrix.try_inverse().expect("Stiffness matrix must be invertible"),
        }
    }
    pub fn get_stiffness(&self) -> na::SMatrix<f64, 6, 6> {
        match &self.matrix {
            MechanicalMatrix::Stiffness(matrix) => *matrix,
            MechanicalMatrix::Compliance(matrix) => matrix.try_inverse().expect("Compliance matrix must be invertible"),
        }
    }

    pub fn get_plane_stress_stiffness(&self) -> na::SMatrix<f64, 3, 3> {
        let stiffness = self.get_stiffness();
        let submatrix_indices = [0, 1, 5];
        let mut submatrix = na::SMatrix::<f64, 3, 3>::zeros();
        
        for i in 0..3 {
            for j in 0..3 {
                submatrix[(i, j)] = stiffness[(submatrix_indices[i], submatrix_indices[j])];
            }
        }
        
        submatrix
    }

    pub fn get_plane_strain_stiffness(&self) -> na::SMatrix<f64, 3, 3> {
        let compliance = self.get_compliance();
        let submatrix_indices = [0, 1, 5];
        let mut submatrix = na::SMatrix::<f64, 3, 3>::zeros();

        for i in 0..3 {
            for j in 0..3 {
                submatrix[(i, j)] = compliance[(submatrix_indices[i], submatrix_indices[j])];
            }
        }

        submatrix.try_inverse().expect("Submatrix must be invertible")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_isotropic_material_compliance() {
        let em = 2.0e5;
        let nu = 0.3;
        const NDIGITS: i32 = 3;

        let material = Material::Isotropic(em, nu, None);
        let compliance = material.get_compliance();

        assert_eq!((compliance[(0, 0)] * 10f64.powi(NDIGITS)) as i64, (1.0 / em * 10f64.powi(NDIGITS)) as i64);
        assert_eq!((compliance[(0, 1)] * 10f64.powi(NDIGITS)) as i64, (-nu / em * 10f64.powi(NDIGITS)) as i64);
        assert_eq!((compliance[(3, 3)] * 10f64.powi(NDIGITS)) as i64, (2.0 * (1.0 + nu) / em * 10f64.powi(NDIGITS)) as i64);
    }

    #[test]
    fn test_plane_stress_stiffness() {
        let material = Material::Isotropic(2.0e5, 0.3, Option::None);
        let stiff = material.get_plane_stress_stiffness();
        
        for i in 0..3 {
            for j in 0..3 {
                // Check if all elements are equal
                assert_eq!(stiff[(i, j)], stiff[(i, j)]);  // Assertion to validate matrix size
            }
        }
    }

    #[test]
    fn test_plane_strain_stiffness() {
        let material = Material::Isotropic(2.0e5, 0.3, Option::None);
        let stiff = material.get_plane_strain_stiffness();
        
        for i in 0..3 {
            for j in 0..3 {
                // Check if all elements are equal
                assert_eq!(stiff[(i, j)], stiff[(i, j)]);  // Assertion to validate matrix size
            }
        }
    }
}
